from pyamf.remoting.client import RemotingService
import classes


def get_videos(channel_id):
	videos = []
	client = RemotingService('http://afl.bigpondvideo.com/App/AmfPhp/gateway.php')
	service = client.getService('Miscellaneous')
	params = {'navId': channel_id, 'startRecord':'0', 'howMany':'50', 'platformId':'1', 'phpFunction':'getClipList', 'asFunction':'publishClipList'}
	print "Videos"
	print "Videos: %s" % service.getClipList({'navId': 10, 'startRecord':'0', 'howMany':'50', 'platformId':'1', 'phpFunction':'getClipList', 'asFunction':'publishClipList'})
	videos_list = service.getClipList(params)
	if videos_list:
		for video_item in videos_list[0]['items']:
			video = parse_video(video_item)
			videos.append(video)
	else:
		print "ERROR: Video list returned no results."

	return videos

def get_video_url(video_id):
	client = RemotingService('http://afl.bigpondvideo.com/App/AmfPhp/gateway.php')
	service = client.getService('SEOPlayer')
	video_high_qual = service.getMediaURL({'cid': video_id})

	return video_high_qual

def parse_video(video_item):
	new_video = classes.Video()
	v = video_item['content']
	print v
	new_video.id = v['contentId']
	new_video.title = v['title']
	new_video.description = v['description']
	new_video.duration = v['duration']
	new_video.thumbnail = v['imageUrl']

	return new_video

