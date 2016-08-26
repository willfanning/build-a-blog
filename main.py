import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


class Post(db.Model):
    title = db.StringProperty(required=True)
    post = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
       self.write(self.render_str(template, **kw))


class Main(Handler):

    def get(self):
        posts = db.GqlQuery('SELECT * FROM Post '
                            'ORDER BY created DESC')
        self.render('blog.html', posts=posts)

    def post(self):
        title = self.request.get('title')
        post = self.request.get('post')

        if title and post:
            p = Post(title=title, post=post)
            p.put()
            self.redirect('/')
        else:
            error = 'Both title and post required'
            self.render('newpost.html', title=title, post=post, error=error)


class NewPost(Handler):
    def get(self):
        self.render('newpost.html')


app = webapp2.WSGIApplication([
    ('/', Main),
    ('/newpost', NewPost)
], debug=True)
