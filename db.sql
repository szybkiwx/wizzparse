create table analytics_view (
	country text, 
	city text, 
	departure datetime, 
	middestination text,
	arrival datetime, 
	carrier_one text,
    carrier_two text, 
	price real,

	ret_departure datetime, 
	ret_middestination text,
	ret_arrival datetime, 
	ret_carrier_one text,
    ret_carrier_two text, 
	ret_price real
); 