import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
from pyecharts.charts import WordCloud, Bar, Line, Pie, Scatter, Radar, Gauge
from pyecharts import options as opts
import re
from streamlit.components.v1 import html

# Streamlit界面设置
st.title('文章URL文本分析')

# 文本输入框
url = st.text_input('请输入文章URL:', '')

if url:
    # 抓取文本内容
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()

        # 去除不必要的字符
        cleaned_text = re.sub(r'\s+', ' ', text).strip()

        # 分词
        words = jieba.lcut(cleaned_text)

        # 过滤掉非汉字字符
        words = [word for word in words if re.match(r'^[\u4e00-\u9fff]+$', word)]

        # 统计词频
        word_counts = Counter(words)

        # 交互式过滤低频词
        min_freq = st.sidebar.slider('最低词频:', 1, max(word_counts.values()), 1)
        filtered_word_counts = {word: count for word, count in word_counts.items() if count >= min_freq}

        # 展示词频排名前20的词汇
        top_words = dict(Counter(filtered_word_counts).most_common(20))
        st.write('词频排名前20的词汇:')
        st.table(top_words)

        # 选择图表类型
        chart_type = st.sidebar.selectbox('选择图表类型:', ['词云', '柱状图', '折线图', '饼图', '散点图', '雷达图', '仪表盘'])

        # 绘制图表
        def render_pyecharts(chart):
            # Render the PyECharts chart using Streamlit's HTML component
            chart_html = chart.render_embed()
            components_html = f"""
                <html>
                    <head><script src="https://cdn.jsdelivr.net/npm/echarts@5.4.2/dist/echarts.min.js"></script></head>
                    <body>
                        {chart_html}
                    </body>
                </html>
            """
            html(components_html, height=600)

        if chart_type == '词云':
            word_cloud = (
                WordCloud()
                .add("", list(top_words.items()), word_size_range=[20, 100])
                .set_global_opts(title_opts=opts.TitleOpts(title="词频词云"))
            )
            render_pyecharts(word_cloud)
        elif chart_type == '柱状图':
            bar_chart = (
                Bar()
                .add_xaxis(list(top_words.keys()))
                .add_yaxis("词频", list(top_words.values()))
                .set_global_opts(title_opts=opts.TitleOpts(title="词频柱状图"))
            )
            render_pyecharts(bar_chart)
        elif chart_type == '折线图':
            line_chart = (
                Line()
                .add_xaxis(list(top_words.keys()))
                .add_yaxis("词频", list(top_words.values()))
                .set_global_opts(title_opts=opts.TitleOpts(title="词频折线图"))
            )
            render_pyecharts(line_chart)
        elif chart_type == '饼图':
            pie_chart = (
                Pie()
                .add("", list(top_words.items()))
                .set_global_opts(title_opts=opts.TitleOpts(title="词频饼图"))
            )
            render_pyecharts(pie_chart)
        elif chart_type == '散点图':
            scatter_chart = (
                Scatter()
                .add_xaxis(list(top_words.keys()))
                .add_yaxis("词频", list(top_words.values()))
                .set_global_opts(title_opts=opts.TitleOpts(title="词频散点图"))
            )
            render_pyecharts(scatter_chart)
        elif chart_type == '雷达图':
            radar_chart = (
                Radar()
                .add_schema(schema=[opts.RadarIndicatorItem(name=key, max_=max(top_words.values())) for key in top_words.keys()])
                .add("词频", [[value for value in top_words.values()]])
                .set_global_opts(title_opts=opts.TitleOpts(title="词频雷达图"))
            )
            render_pyecharts(radar_chart)
        elif chart_type == '仪表盘':
            gauge_data = list(top_words.items())[0]  # 取第一个词作为示例
            gauge_chart = (
                Gauge()
                .add("", [(gauge_data[0], gauge_data[1])])
                .set_global_opts(title_opts=opts.TitleOpts(title=f"词频仪表盘 - {gauge_data[0]}"))
            )
            render_pyecharts(gauge_chart)

    except Exception as e:
        st.error(f'发生错误: {e}')