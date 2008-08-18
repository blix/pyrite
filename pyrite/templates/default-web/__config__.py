
url_map = (
    (r'^$', 'project.html'),
    (r'^(?P<project>.*)/commit/(?P<commit_id>.*)$', 'commit.html'),
    (r'^(?P<project>.*)/tree/(?P<tree_id>.*)\?path=(?P<path>.*)$',
        'tree.html'),
    (r'^(?P<project>.*)/blob/(?P<blob_id>.*)\?path=(?P<path>.*)$',
     'blob.html'),
    (r'^(?P<project>.*)/ref/(?P<ref_id>.*)$', 'ref.html'),
    (r'^(?P<project>[^/]*)$', 'project.html'),
    (r'^(?P<project>.*)/diff/(?P<v1>[a-z0-9]*)/(?P<v2>[a-z0-9]*)/(?P<f>.*)$',
                                                        'diff.html'),
    (r'^(?P<project>.*)/ssdiff/(?P<v1>.*)/(?P<v2>.*)/(?P<f>.*)$',
                                                        'ssdiff.html'),
)

