import pickle
from os import path
import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

comment = []
with open('data2.txt',mode='r',encoding='utf-8') as f:
	rows = f.readlines()
	for row in rows:
		if len(row.split(',')) >= 4:
			comment += row.split(',')[3:]

comment_after_split = jieba.cut(str(comment),cut_all=False)

wl_space_split= " ".join(comment_after_split)
#导入背景图
backgroud_Image = plt.imread('/home/chaos/Pictures/1.png')
stopwords = STOPWORDS.copy()
#可以加多个屏蔽词
stopwords.add("电影")
stopwords.add("一部")
stopwords.add("一个")
stopwords.add("没有")
stopwords.add("什么")
stopwords.add("有点")
stopwords.add("这部")
stopwords.add("这个")
stopwords.add("不是")
stopwords.add("真的")
stopwords.add("感觉")
stopwords.add("觉得")
stopwords.add("还是")
stopwords.add("导演")
stopwords.add("演员")

erasewords = ["最后", "但是", "很多", "所以", "已经", "就是", "之后", "关于", "以为", "一样"]
for i in erasewords:
	stopwords.add(i)

#设置词云参数
#参数分别是指定字体、背景颜色、最大的词的大小、使用给定图作为背景形状
wc = WordCloud(width=1024,height=768,background_color='white',
	mask=backgroud_Image,font_path="/home/chaos/Downloads/fonts/yaheiBold.ttf",
	stopwords=stopwords,max_font_size=250,
	random_state=50)
wc.generate_from_text(wl_space_split)
img_colors= ImageColorGenerator(backgroud_Image)
wc.recolor(color_func=img_colors)
plt.imshow(wc)
plt.axis('off')#不显示坐标轴
plt.show()
#保存结果到本地
wc.to_file('word_yun.jpg')