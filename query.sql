select  f1.start, f1.destination, f2.destination, f1.departure, f2.arrival, f2.carrier, f1.price_pln + f2.price_pln  as p
from flights f1 join flights f2 on f1.destination = f2.start 
and strftime('%s', f2.departure) - strftime('%s', f1.arrival) between 3600 and 43200 and p < 500
and f1.start = 'GDN' and f2.destination = 'VNO'
order by f1.departure;