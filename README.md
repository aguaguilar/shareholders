# Norway shareholders
This application aims serve an interface to save organizations and persons that are able to buy shares.
In addition, serves information about the organization regarding to its own shares such as owners, holdings and a brief summary.


## Rules
* Persons can buy shares for a given organization
* Organizations can buy shares for a given organization
* There are two kind of shares: A-aksjer and B-aksje.

## Resources
* [Norwegian share holder registry](https://www.altinn.no/starte-og-drive/skatt-og-avgift/skatt/aksjonarregisteret/)

## Run the application
`docker-compose up`

## Run test, flake8 and coverage
`docker-compose run test`

## Application
The app was built using:
* Django
* Python 3.9
* PostgreSQL
* MongoDB
* RabbitMQ
* Docker
* Docker Compose

#### Endpoints
* `/api/<orgnr>/owners`

  Returns all registered owners for a company.

  An **owner** is any entity (company _or_ person)
  that holds shares in the company.

* `/api/<orgnr>/holdings`

  Returns all registered holdings a company has in other
  companies.

  A **holding** means the number of/percentage of shares
  a person or company has in another company.

* `/api/<orgnr>/summary`

  Returns a basic summary of a company's ownership,
  as well as some other potentially interesting information.

  A company is thought to have an "interesting" ownership
  structure if there is a foreign entity among its owners.

  A company is also considered interesting if it has multiple
  share classes.
  
* `/api/organization/`

  Allows adding new organization that can buy shares

* `/api/person/`

  Allows adding a new person that can buy shares

* `/api/share/`

  Allow adding new share's purchase

#### Architecture
Keeping in mind that it has to support millions of records (write and read) I decided to use [CQRS pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/cqrs).
CQRS allows us to separate the database write and read operations into two different schemas.
For example, in this application the write operations will be performed in PostgreSQL database and read operations will be performed in MongoDB (NoSQL database).

Using cqrs pattern I get some advantages like:
* Low overload over databases
* Delete lock scenarios when I want to read some row

But, I have some cons:
* I have to embrace the [eventual consistency](https://en.wikipedia.org/wiki/Eventual_consistency). When I save some row in write database I have to wait some delay to have the data available for read operations.

##### How do I deal with latency writing in two datastore?
To keep the write and read datastores sync up I have to perform two write operations.
But it could take long time meanwhile the user is waiting for the response. For example, take a look in the next image
![example1](https://i.ibb.co/0yfQXRQ/d.jpg)

In this scenario the user have to wait until my application save the data into both datastore. 

I performed this operation asyncronhous in order to decrease the latency and the time that the user have to wait for a response from the API.
![example2](https://i.ibb.co/SfvGxzp/d1.jpg)

In this scenario when the data is saved into write only db I send a message trough amqp queue (a.k.a rabbitmq) to save the data into read only database.
I have a listener that receive this operation request and it will perform the write operation in the read-only databse when it can.

Why do I use SQL for write db? Because I can make sure the ACID principles
Why do I use NoSQL for read db? Because those are prepared to read data quickly

## TO DO
* Integration test for rabbitmq and async share saving
* Add TLS encryption for rabbitmq
* Use kubernetes for production environment and secret feature to save sensible data such as secret keys
