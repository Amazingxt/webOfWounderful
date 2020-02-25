# spiderArXiv
Web app based on python flask and bootstrap. There are three modules in this web, including article spider, storehouse management and format transformation of article. To run this app, typing "python Info.py" in the bash and this app will run in the url: http://localhost:5000

The organization structure of this project:


	arXiv/
			items.py
			middleware.py
			pipelines.py
			settings.py
			spiders/
					quantum_article.py		
	DataBase/
			2020-2-22-articles.db
			equipmentInfo.db
			personQueryInfo.db
	Web/
			info.py
			static/
					equipmentFiles/
					webFigs/
			templates/
	Query.py
	Send_Info.py
	spiderArXiv.py

1、文章爬取

​	web端在 ./Web 文件夹，爬虫在 ./arXiv 文件夹，主程序在根目录。首先在 根目录 文件夹下运行 scrapy crawl quantum_article 爬取当日文章信息并把信息存储在 DataBase 文件夹下。Web 网页会收集用户需求，存储在 DataBase 文件夹下。每当运行根目录下的 python spiderArXiv.py ，就会匹配文章与用户的信息，进行邮件发送

2、仓库管理

​	在 Web 文件夹下执行 flask Info.py ，运行网页端，static静态文件夹用于存放网页或者上传的文件，templates 用于处理Info文件中需要渲染的html。