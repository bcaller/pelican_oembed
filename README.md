# pelican_oembed
Python Pelican extension for embedding content using OEmbed in Markdown

Embed any [oembed](http://www.oembed.com/) content with the `[!embed](url)` tag.

[![travis](https://travis-ci.org/bcaller/pelican_oembed.svg)](https://travis-ci.org/bcaller/pelican_oembed)

## Photos and rich html

Embeddable content could be Flickr photos, Twitter statuses or Youtube videos ([list of services](http://www.oembed.com/)).
When not a video, we use the included dependency [pyembed-markdown](https://github.com/pyembed/pyembed-markdown) to call the oembed service and convert
```
[!embed](https://www.flickr.com/photos/bees/74/)
```
to
```
<img src="https://farm1.staticflickr.com/1/74_ddb152d117.jpg" width="500" height="375" />
```

## Videos

However, when you embed videos, you expose your users to tracking by extenal sites.
So with this plugin, if a video thumbnail is available, it is shown first **instead of the iframe**.

Embed content with:

```
[!embed](https://www.youtube.com/watch?v=jNQXAC9IVRw)
```

and it will be turned into:

```
<img class="oembed-preview" data-content="<iframe width=&quot;459&quot; height=&quot;344&quot; src=&quot;https://www.youtube.com/embed/jNQXAC9IVRw?feature=oembed&quot; frameborder=&quot;0&quot; allowfullscreen></iframe>" title="Me at the zoo" src="https://i.ytimg.com/vi/jNQXAC9IVRw/hqdefault.jpg" width="480" height="360" />
```

rather than:

```
<iframe width="459" height="344" src="http://www.youtube.com/embed/jNQXAC9IVRw?feature=oembed" frameborder="0" allowfullscreen></iframe>
```

Javascript should be added to the page to show the video (in the `data-content` attribute) upon clicking the image (see examples folder).
The actual output can be controlled with the `OEMBED_VIDEO_FORMAT` config variable which can be a percent-string or function taking an oembed parameter dictionary.


The thumbnails can be stored in your output directory to further increase privacy, by including the `OEMBED_THUMBNAIL_SAVE_AS` and optionally `OEMBED_THUMBNAIL_URL` config variables.

## Caching

If you have many posts with embedded videos, you would need to make many requests on compilation.
Instead, all oembed requests can be cached simply by specifying a `OEMBED_CACHE_FILE` variable.

# Installation

```
git clone https://github.com/bcaller/pelican_oembed.git
pip install -e pelican_oembed
```

Then add `pelican_oembed` to `PLUGINS` in your config file. See the examples folder for usage e.g. setting up the cache.

## Test
`python setup.py test` 

Enjoy! Happy to accept feedback or modifications.
