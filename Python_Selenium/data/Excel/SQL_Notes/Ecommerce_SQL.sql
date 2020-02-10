/****** Script for SelectTopNRows command from SSMS  ******/
SELECT TOP 1000 [department]
      ,[category]
      ,[sub_category]
      ,[product_location]
      ,[product_name]
      ,[product_description]
      ,[product_current_price]
      ,[product_discount]
      ,[number_of_customer_reviews]
      ,[product_page_url]
      ,[product_url_link]
      ,[product_selection_xpath]
      ,[examples_notes]
  FROM [Ecommerce_Retailers].[dbo].[product_selection] ORDER BY department

!-- SELECT * FROM [Ecommerce_Retailers].[dbo].[product_selection] WHERE product_name='Product Name' and product_description='Product Description' 

!-- DELETE FROM [Ecommerce_Retailers].[dbo].[product_selection] WHERE product_name='Product Name' and product_description='Product Description' 