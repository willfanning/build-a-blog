import os
import webapp2
import jinja2

from random import choice
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


def get_posts(limit, offset):
    return db.GqlQuery('SELECT * FROM Post ORDER BY submitted DESC LIMIT {} OFFSET {}'.format(limit, offset))


def get_random_post():
    posts = list(db.GqlQuery('SELECT * FROM Post'))
    post = choice(posts)
    post_id = post.key().id()
    return str(post_id)


def get_post_ids():
    posts = list(db.GqlQuery('SELECT * FROM Post'))
    return [post.key().id() for post in posts]


class Post(db.Model):
    title = db.StringProperty(required=True)
    post = db.TextProperty(required=True)
    submitted = db.DateTimeProperty(auto_now_add=True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class Blog(Handler):
    def get(self):
        limit = 5
        offset = 0
        page = self.request.get('page')

        if (not page) or (int(page) == 1):
            page = 1
        else:
            offset = (limit * int(page)) - limit
            page = int(page)

        posts = get_posts(limit, offset)
        num_posts = posts.count()
        post_range = num_posts - offset

        if post_range > limit:
            post_range = limit
        else:
            pass
        self.render('blog.html',
                    posts=posts,
                    page=page,
                    limit=limit,
                    offset=offset,
                    num_posts=num_posts,
                    post_range=post_range,
                    main_page=True
                    )


class NewPost(Handler):
    def render_newpost(self, title='', post='', error=''):
        self.render('newpost.html', title=title, post=post, error=error)

    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get('title')
        post = self.request.get('post')

        if title and post:
            p = Post(title=title, post=post)
            p.put()
            post_id = str(p.key().id())
            self.redirect('/blog/' + post_id)
        else:
            error = 'Both title and post required'
            self.render_newpost(title, post, error)


class ViewPost(Handler):
    def get(self, post_id):
        if int(post_id) in get_post_ids():
            post = Post.get_by_id(ids=int(post_id))
            self.render('blog.html', posts=[post])
        else:
            self.redirect('/')


class Random(Handler):
    def get(self):
        self.redirect('/blog/' + get_random_post())


app = webapp2.WSGIApplication([
    ('/', Blog),
    ('/blog', Blog),
    ('/random', Random),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<post_id:\d+>', ViewPost)
], debug=True)
