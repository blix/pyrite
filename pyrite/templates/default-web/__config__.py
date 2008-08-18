
url_map = (
    (r'^$', 'project.html'),
    (r'^(?P<project>[^/]*)/?(?P<page>[0-9]*)$', 'project.html'),
    (r'^(?P<project>.*)/commit/(?P<commit_id>.*)$', 'commit.html'),
    (r'^(?P<project>.*)/tree/(?P<commit_id>[a-z0-9]*)/(?P<tree_id>.*)'
        '\?path=(?P<path>.*)$', 'tree.html'),
    (r'^(?P<project>.*)/blob/(?P<commit_id>[a-z0-9]*)/(?P<blob_id>.*)'
     '\?path=(?P<path>.*)$', 'blob.html'),
    (r'^(?P<project>.*)/ref/(?P<ref_id>[^/]*)/?(?P<page>[0-9]*)$',
                                                        'ref.html'),
    (r'^(?P<project>.*)/diff/(?P<v1>[a-z0-9]*)/(?P<v2>[a-z0-9]*)'
        '/?(?P<f>.*)$', 'diff.html'),
    (r'^(?P<project>.*)/ssdiff/(?P<v1>.*)/(?P<v2>.*)/(?P<f>.*)$',
                                                        'ssdiff.html'),
    (r'^(?P<project>.*)/reflist/(?P<type>.*)$', 'all_type_refs.html'),
    (r'^(?P<project>.*)/blame/(?P<commit_id>[a-z0-9]*)'
        '\?path=(?P<path>.*)$', 'blame.html'),
    # add line for tag viewer ()
)

