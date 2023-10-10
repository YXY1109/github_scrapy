import datetime

from sqlalchemy.orm import declarative_base, sessionmaker

from sqlalchemy import String, Column, Text, DateTime, create_engine

Base = declarative_base()


class Article(Base):
    __tablename__ = 'cn_article'

    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    url_object_id = Column(String(50), primary_key=True)
    front_image_url = Column(String(255), nullable=False)
    front_image_path = Column(String(255), nullable=False)
    create_time = Column(DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f"文章标题：{self.title}"


class MySession(object):
    def __init__(self):
        # 创建mysql连接引擎
        engine = create_engine("mysql+pymysql://root:root@127.0.0.1:3306/github_spider",
                               echo=True)
        # 创建表
        Base.metadata.create_all(engine, checkfirst=True)
        # 创建mysql的session连接对象
        self.session = sessionmaker(bind=engine)()


if __name__ == '__main__':
    session = MySession().session
    article = Article(title="测试", content="测试", url_object_id="测试1", front_image_url="测试",
                      front_image_path="测试")
    session.add(article)
    session.commit()
