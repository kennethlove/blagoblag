import datetime
import os

from liquidluck.options import settings, g
from liquidluck.readers.base import Post
from liquidluck.readers.restructuredtext import RestructuredTextReader
from liquidluck.writers import core
from liquidluck.writers.base import Pagination, get_post_slug


class DateFromPathPost(Post):
    MONTHS_BY_NAME = {
        "jan": 1,
        "feb": 2,
        "mar": 3,
        "apr": 4,
        "may": 5,
        "jun": 6,
        "jul": 7,
        "aug": 8,
        "sep": 9,
        "oct": 10,
        "nov": 11,
        "dec": 12,
    }

    @property
    def date(self):
        if "blog" not in self.filepath:
            # Posts don't have a date
            return None
        _, _, year, month_name, day, _ = self.filepath.split("/", 6)
        month = self.MONTHS_BY_NAME[month_name]
        return datetime.date(int(year), int(month), int(day))

    @property
    def month_name(self):
        return self.date.strftime("%b").lower()


class DateFromPathRestructuredTextReader(RestructuredTextReader):
    post_class = DateFromPathPost


def get_post_destination(post, slug_format):
    slug = get_post_slug(post, slug_format)

    if slug.endswith('.html'):
        return slug
    elif slug.endswith("/"):
        return slug + 'index.html'
    else:
        return slug + '.html'


class DirectoryPostWriter(core.PostWriter):
    def _dest_of(self, post):
        dest = get_post_destination(post, settings.config['permalink'])
        return os.path.join(g.output_directory, dest)


class DirectoryPageWriter(core.PageWriter):
    def start(self):
        l = len(g.source_directory) + 1
        for post in g.pure_pages:
            template = post.template or self._template
            filename = os.path.splitext(post.filepath[l:])[0] + '/index.html'
            dest = os.path.join(g.output_directory, filename)
            self.render({'post': post}, template, dest)


class DirectoryArchiveWriter(core.ArchiveWriter):
    def start(self):
        pagination = Pagination(g.public_posts, 1, self.perpage)
        pagination.title = self._title
        pagination.root = self.prefix_dest('')

        dest = os.path.join(g.output_directory, self._output)
        self.render({'pagination': pagination}, self._template, dest)

        if pagination.pages < 2:
            return

        for page in range(1, pagination.pages + 1):
            pagination = Pagination(g.public_posts, page, self.perpage)
            pagination.title = self._title
            pagination.root = self.prefix_dest('')
            dest = os.path.join(g.output_directory, 'page/%s/index.html' % page)
            if pagination.root:
                dest = os.path.join(
                    g.output_directory,
                    pagination.root,
                    'page/%s/index.html' % page
                )
            self.render({'pagination': pagination}, self._template, dest)


class DirectoryYearWriter(core.YearWriter):
    def _write_posts(self, year):
        posts = self._posts[year]
        pagination = Pagination(posts, 1, self.perpage)
        pagination.title = year
        pagination.root = self.prefix_dest(year)

        dest = os.path.join(g.output_directory, pagination.root, 'index.html')
        self.render({'pagination': pagination}, self._template, dest)

        if pagination.pages < 2:
            return

        for page in range(1, pagination.pages + 1):
            pagination = Pagination(posts, page, self.perpage)
            pagination.title = year
            pagination.root = self.prefix_dest(year)

            dest = os.path.join(
                g.output_directory,
                pagination.root,
                'page/%s/index.html' % page
            )
            self.render({'pagination': pagination}, self._template, dest)
