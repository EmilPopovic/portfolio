---

slug: "my-blog"
file: "my-blog.md"
title: "My Overengineered Little Blog"
authors: ["Emil Popović"]
created: "2025-09-13"
description: "This was supposed to be simple..."
tags: ["tech", "python", "web-development"]
draft: false
featured: false

---

Welcome to my first ever blog post, I guess... This is the first in a [series](https://emilpopovic.me/blog/s/project-summaries) of posts in which I will be writing about some of my projects... And that is why this site exists! So I can share my stuff with people who find it interesting.

In this post, I'll walk through how I built my personal website and blog system, and why I probably over-engineered it.

Before jumping into writing code, I started to thing about the requirements for my personal site. I knew I wanted a blog section where I could organize posts into series, inspired by sequences on [LessWrong](https://www.lesswrong.com/rationality). Why? Because I want my readers to be able to follow a specific project without the hassle of searching in a disorganized sea of [All Posts](https://emilpopovic.me/blog). That means that if you are interested in, for example, the project of running an OS on a custom RISC-V processor, you can simply go to that series, open a post, and keep clicking on *Next post* to read more.

## The Blog

The series mechanic turned out to be quite a bit more complicated than I expected. Just think about it, what should the URL of a post in a series be? I was intimately aware of that problem long before I started working on this site. That is, when I tried to [scrape all of LessWrong](https://github.com/EmilPopovic/lw-scraper) and make it explorable through a graph, where posts are connected if one links to the other, or they are part of the same sequence. The problem was that a single post could have multiple URLs (for example a standalone URL, sequence URL and legacy URL), without an easy way of finding out the other ones upon stumbling on the post through a breadth-first crawl. That makes it impossible to find out all information about a post in a single visit. *Not on my blog.*

Here is how I designed it: each post has a `/blog/p/{post_slug}` URL (call it a *standalone post* URL). If a post is in one or more series, there is also `/blog/s/{serie_slug}/p/{post_slug}` (call it a *series post* URL) for every series the post is part of. And this is how I fixed the LessWrong issue - when viewing the post *standalone* (without next and previouos posts), there are links to view the post as part of a series, and if you are viewing the post *in a series*, you can choose to view it standalone. That way, it is possible to easily find out all series a post is a part of.

The way I designed it, posts and series are just [Markdown](https://en.wikipedia.org/wiki/Markdown) and [YAML](https://en.wikipedia.org/wiki/YAML) files. Information and metadata about them is stored in *frontmatter* (in YAML) at the beginning of the file, separated by `---`, like this (for this post):

```yaml
---

slug: "my-blog"
file: "my-blog.md"
title: "My Overengineered Little Blog"
authors: ["Emil Popović"]
created: "2025-09-13"
description: "This was supposed to be simple..."
tags: ["tech", "python", "web-development"]
draft: false
featured: false

---

Here goes post content
```

See, a post does not mention series anywhere. Series decide which posts they include, and posts *do not* decide in which series they can be found. A series is a YAML file (like the frontmatter of a post, but without any content), like this:

```yaml
slug: project-summaries
title: "Project Summaries"
description: "The things I have been working on"
authors: ["Emil Popović"]
created: "2025-09-12"
status: ""
cover_image: ""
posts:
  - slug: "my-blog"
    order: 1
```

"But I am viewing a website right now, it is all HTML! Where did that come from?" I hear you, and this is how these Markdown files are converted to HTML to be sent to your browser...

## Templates

As the subtitle of this post says, this was supposed to be simple - no databases, convoluted [frameworks](https://react.dev/), thousands of lines of client-side Javascript; just Markdown files and [Jinja2](https://en.wikipedia.org/wiki/Jinja_(template_engine)) templates. That way, a page may look something like this (in this case, the [about](https://emilpopovic.me/about) page):

```html
{% from "partial/icon.html" import icon %}
<!DOCTYPE html>
<html lang="en">
  <head>
    {% include "partial/meta.html" %}
  </head>
  <body>
    <main class="main-wrapper">
      <a href="/" class="back-link">{{ icon("arrow_back", size="16") }}Back to Home</a>
      <div class="post-body">
        {{ about | safe }}
      </div>
      {% include "partial/theme_switch.html" %}
    </main>
  </body>
</html>

```

It is mostly HTML, with dynamically generated content inside `{ }` sprinkled on top. The Python [FastAPI](https://fastapi.tiangolo.com/) backend can retrieve the requested post, load the metadata into a `Post` object, get the `.md` file from the filesystem, convert the Markdown into HTML using the `markdown` library, insert the newly generated HTML content into a template, and finally send it to the reader. The entire ordeal may look something like this:

```py
# When a GET request is sent to /blog/p/ with a given post_slug
@router.get('/blog/p/{post_slug}', response_class=HTMLResponse)
async def post(
    request: Request,
    post_slug: str,
    blog_service: BlogService = Depends(get_blog_service),
    template_service: TemplateService = Depends(get_template_service)
):
    # Use the blog service to get a post object
    post: Post = blog_service.get_post(post_slug)
    # If the post does not exist, show an error
    if not post:
        raise HTTPException(status_code=404, detail='Post not found')
    
    # Use the blog service to convert the post content into HTML
    html_body: str = blog_service.render_post_body(post)
    # Use the blog service to find out which series a post is in
    series_list: list[Series] = blog_service.get_series_of_post(post_slug)

    # Use the template service to render the entire page with the data of the requested post and send it to the reader
    return template_service.render_post(
        {
            'post': post,
            'body': html_body,
            'series_list': series_list,
            'current_series': None,
            'navigation': None,
            'title': post.title
        },
        request
    )
```

Nothing is done client-side. The only requests the browser sends is for the HTML page, needed CSS, and fonts. No Javascript needed.

But what if you find this so interesting you just have to reach out? This is how it works...

## Reaching Out

You can find all the usual info like my [email](mailto:mail@emilpopovic.me), [LinkedIn](https://www.linkedin.com/in/emilpopovic/), and [GitHub](https://github.com/EmilPopovic) on the [contact](https://emilpopovic.me/contact) page. But look at that curious thing, there is a contact form! It is for sure using a third-party privacy-invasive form notification thing. No, *that is completely custom, too*.

When you click the *Send* button, that sends your message via a `POST` request to the backend which uses the custom email service to send me an email, and renders you a beautiful response page.

The email is sent by my self-hosted email server (using [Docker Mailserver](https://github.com/docker-mailserver/docker-mailserver)) which my apps use to send me notifications.

---

And that is pretty much it! (If we ignore a lot of CSS...) As my home server is set up to deploy all services using [Docker Compose](https://docs.docker.com/compose/), every time a new commit is pushed to the `main` branch, a new Docker image is built and pushed to [GHCR](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#about-the-container-registry). That push is detected by [Watchtower](https://github.com/containrrr/watchtower), and the changes are deployed on the server.
