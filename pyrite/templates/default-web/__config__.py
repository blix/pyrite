
url_map = (
    (r'^$', 'project.html'),
    (r'^(?P<project>.*)/commit/(?P<commit_id>.*)$', 'commit.html'),
    (r'^(?P<project>.*)/tree/(?P<tree_id>[a-z0-9]*)\?path=(?P<path>.*)$',
        'tree.html'),
    (r'^(?P<project>.*)/blob/(?P<blob_id>[a-z0-9]*)\?path=(?P<path>.*)$',
     'blob.html'),
    (r'^(?P<project>.*)/ref/(?P<ref_id>[a-z0-9]*)$', 'ref.html'),
)

