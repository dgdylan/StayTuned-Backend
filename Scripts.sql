#Create Schema
CREATE DATABASE `project`;


#Create email_requests table
CREATE TABLE `email_requests` (
	`customer_id` INT NOT NULL AUTO_INCREMENT
	,`product_id` INT NOT NULL
	,`email_address` VARCHAR(100) NOT NULL
	,`first_name` VARCHAR(45) NOT NULL
	,`last_name` VARCHAR(45) NOT NULL
	,`price_at_moment` DECIMAL(10, 2) NOT NULL
	,`email_sent` TINYINT DEFAULT '0'
	,PRIMARY KEY (`customer_id`)
	,KEY `product_id_idx`(`product_id`)
	,CONSTRAINT `product_id` FOREIGN KEY (`product_id`) REFERENCES `product`(`product_id`)
	) ENGINE = InnoDB AUTO_INCREMENT = 18 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;


#Create product table
CREATE TABLE `product` (
	`product_id` INT NOT NULL AUTO_INCREMENT
	,`product_model_number` VARCHAR(45) NOT NULL
	,`product_brand` VARCHAR(45) NOT NULL
	,`product_name` VARCHAR(100) NOT NULL
	,`product_desc` VARCHAR(255) DEFAULT NULL
	,`product_price` DECIMAL(10, 2) NOT NULL
	,`product_discount_pctg` DECIMAL(5, 4) DEFAULT '0.0000'
	,`quantity` INT NOT NULL
	,`img_name` VARCHAR(100) DEFAULT NULL
	,PRIMARY KEY (`product_id`)
	,UNIQUE KEY `product_id_UNIQUE`(`product_id`)
	) ENGINE = InnoDB AUTO_INCREMENT = 14 DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;


#Add product to product table
INSERT INTO `project`.`product` (
	`product_model_number`
	,`product_brand`
	,`product_name`
	,`product_price`
	,`quantity`
	,`img_name`
	)
VALUES (
	'Model Number'
	,'Brand'
	,"Item Name"
	,0.00
	,#Price 0
	,#Quantity 'ImageName.jpg'
	)


#Add discount
UPDATE product SET product_discount_pctg = 0.00 WHERE product_id = 0;


#Query to check if there are any emails ready to be sent
SELECT a.customer_id
	,a.product_id
	,a.email_address
	,CONCAT (
		a.first_name
		,' '
		,a.last_name
		) AS full_name
	,a.price_at_moment
	,CAST((b.product_price - (b.product_price * b.product_discount_pctg)) AS DECIMAL(10, 2)) AS current_sale_price
	,CAST((a.price_at_moment - (b.product_price - (b.product_price * b.product_discount_pctg))) AS DECIMAL(10, 2)) AS sale
	,b.product_brand
	,b.product_name
FROM project.email_requests AS a
INNER JOIN project.product AS b ON a.product_id = b.product_id
WHERE (a.price_at_moment - (b.product_price - (b.product_price * b.product_discount_pctg))) >= 1
	AND a.email_sent = 0;

