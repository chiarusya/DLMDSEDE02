# DLMDSEDE02
Project Data Engineering
Build a real-time data backend for a data-intensive application
Conception Phase

The project will simulate the real-time live tracking of aircraft positioning via ADS-B data, similar to that of the Flightradar24.com website. Flightradar24.com tracks approximately 200,000 flights per day with over 40,000 receivers. Each aircraft transmits its position every second. In the absence of a real ADS-B dataset, a fictitious dataset will be generated by a Python script with a .CSV output. It will then be fed in micro-batches with a time delay to simulate real-time data streaming. 

The data will be processed by Apache Kafka, feeding the data into a web-based application for visually tracking the aircraft on the map. Additionally, the data should be stored in a Postgres database for future analysis. All components will be run as Docker containers, making the project reproducible:

 
1.	Data-generator
2.	Zookeeper 
3.	Kafka
4.	Kafka producer
5.	Kafka consumer
6.	WebSocket server
7.	Frontend app
8.	Postgres DB
 

Each container can be easily managed and developed independently, thereby facilitating the CI/CD pipeline.

The whole architecture can be scaled up by adding more Kafka producer and consumer containers and grouping them. 

Audit logs will be implemented throughout the project to enable performance monitoring. 

Security and access control can be managed via Kafka's built-in security features like ACLs (Access Control Lists). Access to the Postgres DB can be set up based on the user role. Firewall rules can be used for network security. 

•	Data Governance can be set up with the help of Kafka retention policies and Postgres DB data retention policies.
