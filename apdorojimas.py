from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import os



spark = SparkSession.builder.appName("RetailCSV").getOrCreate()

path = r"C:\Users\mangi\PycharmProjects\Job-Offer-Skill-Mapping-Scrapper-ML-\CVB_IT.csv"

df = spark.read.csv(path, header=True, inferSchema=True)

table = "cvb_it_tvarkyta"
df.createOrReplaceTempView(table)

CVB_IT_sutvarkyta = df.dropDuplicates(["url"])

CVB_IT_sutvarkyta.toPandas().to_csv("CVB_IT_tvarkyta.csv", index=False, encoding="utf-8-sig")
