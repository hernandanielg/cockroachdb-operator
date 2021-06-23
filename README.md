# cockroachdb

## Description

CockroachDB it’s a distributed relational database, it’s written in Go language 

It’s cross-platform (Runs on Windows, Mac and Linux)

Brings the best of both Databases worlds

* Scale
* Consistency
* Resiliency
* SQL (ACID guaranteed)

Uses PostgreSQL wire protocol 

PostgreSQL Compatibility  
https://www.cockroachlabs.com/docs/stable/postgresql-compatibility.html


## Usage

First we need to build the charm

```
charmcraft pack
```

### Deploy

Spin up a three units cluster

```
juju deploy -n 3 ./cockroachdb-operator.charm --resource cockroachdb-image=cockroachdb/cockroach:v21.1.1
```

### Initialize CockroachDB cluster
```
juju run-action cockroachdb-operator/leader init --wait
```

### Access CockroachDB Dashboard

We can use any cluster node IP address and access it via following URL

`http://\<Any Cockroach Cluster Node IP Address\>:8080`


Or we can use `nginx-ingress-integrator`

```
juju deploy nginx-ingress-integrator
juju relate cockroachdb-operator nginx-ingress-integrator
```

Change ingress class to public

```
juju config nginx-ingress-integrator ingress-class="public"
```

Add `cockroachdb.juju` entry in your `/etc/hosts`
```
echo "127.0.1.1 cockroachdb.juju" | sudo tee -a /etc/hosts
```


## Developing

Create and activate a virtualenv with the development requirements:

    virtualenv -p python3 venv
    source venv/bin/activate
    pip install -r requirements-dev.txt

## Testing

The Python operator framework includes a very nice harness for testing
operator behaviour without full deployment. Just `run_tests`:

    ./run_tests
