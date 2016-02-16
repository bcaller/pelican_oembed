# Store thumbnails
OEMBED_THUMBNAIL_SAVE_AS = 'img/oembed/%s'

# Enable caching of oembed requests
OEMBED_CACHE_FILE = '.oembed'

# Optionally modify the default code
OEMBED_VIDEO_FORMAT = '<div class="oembed-holder" ' \
                      'style="width:%(thumbnail_width)spx;height:%(thumbnail_height)spx;">' \
                      '<img data-content="%(encoded_html)s" title="%(encoded_title)s" ' \
                      'src="%(thumbnail_url)s" width="%(thumbnail_width)s" height="%(thumbnail_height)s" />' \
                      '<span class="preview-click">Click to play</span></div>'

# PLUGINS = [
#     'pelican_oembed'
# ]

# Include the .js and .css files in your theme
