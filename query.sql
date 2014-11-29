select  f1.start, f1.destination, f2.start, f2.destination, f1.departure, f1.arrival, f1.carrier, f1.price, f2.departure, f2.arrival, f2.carrier, f2.price 
from flights f1 join flights f2 on f1.destination = f2.start 
and strftime('%s', f2.departure) - strftime('%s', f1.arrival) between 3600 and 14400 
and f1.start = 'GDN' limit 1000;