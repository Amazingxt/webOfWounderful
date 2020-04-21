# encoding:utf-8

from __future__ import print_function
import Query as Qu
import Send_Info as Se
import pprint
import re
import datetime

i = datetime.datetime.now()

dbName = "./DataBase/articleDatabase/personQueryInfo.db"


def get_articleInfo():

    articles = Qu.Query_articleInfo()
    articles.connect_db()
    articleKeys = articles.get_keys()
    articleInfo = articles.query_info(articleKeys)
    articles.close_db()
    return articleInfo


def get_personsInfo(dbName):

    persons = Qu.Query_personInfo(dbName)
    persons.connect_db()
    personsKeys = persons.get_keys()
    personsInfo = persons.query_info(personsKeys)
    persons.close_db()
    return personsInfo


def find_Infointerset(articleInfo, personsInfo):

    personIndex = {}
    for person_key, person_value in personsInfo["keyWords"].items():

        # 如果 person_value 是空的则跳过
        if person_value == '':
            continue

        for title_key, title_value in articleInfo["title"].items():

            # 选定文章和个人信息匹配的方式（title）：
            # if ((len(re.findall(person_value + ' ', title_value, flags=re.IGNORECASE)) +
            #      len(re.findall(' ' + person_value + ' ', title_value, flags=re.IGNORECASE)) +
            #         len(re.findall(' ' + person_value, title_value, flags=re.IGNORECASE))) > 0):
            if (
                len(
                    re.findall(
                        " " + person_value + " ", title_value, flags=re.IGNORECASE
                    )
                )
                > 0
            ):

                try:
                    personIndex[person_key].add(title_key)
                except:
                    personIndex[person_key] = set()
                    personIndex[person_key].add(title_key)

    for person_key, person_value in personsInfo["keyWords"].items():

        # 如果 person_value 是空的则跳过
        if person_value == '':
            continue

        for abs_key, abs_value in articleInfo["abstract"].items():

            # 选定文章和个人信息匹配的方式（title）：
            # if (len(re.findall(person_value + ' ', str(abs_value), flags=re.IGNORECASE)) +
            #     len(re.findall(' ' + person_value + ' ', str(abs_value), flags=re.IGNORECASE)) +
            #         len(re.findall(' ' + person_value, str(abs_value), flags=re.IGNORECASE)) > 0):
            if (
                len(
                    re.findall(
                        " " + person_value + " ", str(abs_value), flags=re.IGNORECASE
                    )
                )
                > 0
            ):

                try:
                    personIndex[person_key].add(abs_key)
                except:
                    personIndex[person_key] = set()
                    personIndex[person_key].add(abs_key)

    for person_key, person_value in personsInfo["authors"].items():

        # 如果 person_value 是空的则跳过
        if person_value == '':
            continue

        for author_key, author_value in articleInfo["authors"].items():

            if re.findall(person_value, author_value, flags=re.IGNORECASE):

                try:
                    personIndex[person_key].add(author_key)

                except:
                    personIndex[person_key] = set()
                    personIndex[person_key].add(author_key)

    return personIndex


def merge_Info(articleInfo, index):

    # index = list(index)
    cutline = "--------------------------------------------------------------\n"
    infomation = ""
    for ind in index:
        title = articleInfo["title"][ind]
        authors = articleInfo["authors"][ind]
        abstract = articleInfo["abstract"][ind]
        url = articleInfo["url"][ind]
        info = ("title: %s\n" + "authors: %s\n" + "url: %s\n" + "abstract: %s\n") % (
            title,
            authors,
            url,
            abstract,
        ) + cutline
        infomation += info
    return infomation


def draw_Info(articleInfo, personsInfo, personIndex):

    Infos = {}
    for index, article_indexs in personIndex.items():
        articleIndex = []
        Info = {}
        # 由于 web 端选择领域的时候，arxiv项目前边都加了arxiv,匹配的时候要去掉
        if personsInfo["major"][index][:5] == "arXiv":
            personsInfo["major"][index] = personsInfo["major"][index][6:]

        for article_index in article_indexs:
            if personsInfo["major"][index] == articleInfo["major"][article_index]:
                articleIndex.append(article_index)
        infomation = merge_Info(articleInfo, articleIndex)
        Info[personsInfo["email"][index]] = infomation
        Infos[personsInfo["major"][index]] = Info

    return Infos


def send_emails(Infos):

    today = str(i.year) + "-" + str(i.month) + "-" + str(i.day)

    for major, Info in Infos.items():
        subject = "arXiv articles on " + major + ' in ' + today
        for email, info in Info.items():
            print(email)
            s1 = Se.Send_Email(email)
            s1.send_info(info, subject)


if __name__ == "__main__":

    articleInfo = get_articleInfo()
    personsInfo = get_personsInfo(dbName)
    personIndex = find_Infointerset(articleInfo, personsInfo)
    Info = draw_Info(articleInfo, personsInfo, personIndex)
    # pprint.pprint(Info)
    # print Info
    send_emails(Info)
    # print personIndex
    # print personsInfo['email']
    # s1 = Se.Send_Email(receivers)
    # s1.send_info(self, mainText, subject)
