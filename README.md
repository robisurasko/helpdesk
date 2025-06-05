<div align="center" markdown="1">

<img src=".github/hd-logo.svg" alt="Frappe Helpdesk logo" width="80"/>
<h1>Helpdesk</h1>

**Customer Service, Made Simple and Effective**

![GitHub release (latest by date)](https://img.shields.io/github/v/release/frappe/helpdesk)
[![codecov](https://codecov.io/github/frappe/helpdesk/branch/develop/graph/badge.svg?token=8ZXHCY4G9U)](https://codecov.io/github/frappe/helpdesk)

<a href="https://trendshift.io/repositories/12764" target="_blank"><img src="https://trendshift.io/api/badge/repositories/12764" alt="teableio%2Fteable | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
</div>

</div>


<div align="center">
	<img src="./.github/Hero2.png" alt="Hero Image" width="100%" />
</div>
<br />
<div align="center">
	<a href="https://frappe.io/helpdesk">Website</a>
	-
	<a href="https://docs.frappe.io/helpdesk">Documentation</a>
</div>

## Frappe Helpdesk
Helpdesk is an 100% open-source Ticket Management tool which helps you  streamline your company's support, offers an easy setup, clean user interface, and automation tools to resolve customer queries efficiently.



### Under the Hood

- [**Frappe Framework**](https://github.com/frappe/frappe): A full-stack web application framework written in Python and Javascript.

- [**Frappe UI**](https://github.com/frappe/frappe-ui): A Vue-based UI library, to provide a modern user interface. 


## Production Setup

### Managed Hosting

You can try [our cloud](https://superapp.rndsolusi.com/helpdesk/signup), a simple and user-friendly

It takes care of installation, setup, upgrades, monitoring, maintenance and support of your Frappe deployments. It is a fully featured developer platform with an ability to manage and control multiple Frappe deployments.

### Self Hosting

Follow these steps to set up Frappe Helpdesk in production:

**Step 1**: Download the easy install script

```bash
wget https://frappe.io/easy-install.py
```

**Step 2**: Run the deployment command

```bash
python3 ./easy-install.py deploy \
    --project=helpdesk_prod_setup \
    --email=your_email.example.com \
    --image=ghcr.io/frappe/helpdesk \
    --version=stable \
    --app=helpdesk \
    --sitename subdomain.domain.tld
```

Replace the following parameters with your values:
- `your_email.example.com`: Your email address
- `subdomain.domain.tld`: Your domain name where Helpdesk will be hosted

The script will set up a production-ready instance of Frappe Helpdesk with all the necessary configurations in about 5 minutes.

## Development Setup

### Docker

You need Docker, docker-compose and git setup on your machine. Refer [Docker documentation](https://docs.docker.com/). After that, follow below steps:

**Step 1**: Setup folder and download the required files

    mkdir frappe-helpdesk
    cd frappe-helpdesk

    # Download the docker-compose file
    wget -O docker-compose.yml https://raw.githubusercontent.com/frappe/helpdesk/develop/docker/docker-compose.yml

    # Download the setup script
    wget -O init.sh https://raw.githubusercontent.com/frappe/helpdesk/develop/docker/init.sh

**Step 2**: Run the container and daemonize it

    docker compose up -d

**Step 3**: The site [http://helpdesk.localhost:8000/helpdesk](http://helpdesk.localhost:8000/helpdesk) should now be available. The default credentials are:
- Username: Administrator
- Password: admin

### Local

To setup the repository locally follow the steps mentioned below:

1. Install bench and setup a `frappe-bench` directory by following the [Installation Steps](https://frappeframework.com/docs/user/en/installation)
1. Start the server by running `bench start`
1. In a separate terminal window, create a new site by running `bench new-site helpdesk.test`
1. Map your site to localhost with the command `bench --site helpdesk.test add-to-hosts`
1. Get the Helpdesk app. Run `bench get-app https://github.com/frappe/helpdesk` or `bench get-app --branch main helpdesk https://github.com/robisurasko/helpdesk.git`
1. Run `bench --site helpdesk.test install-app helpdesk`.
1. Now open the URL `http://helpdesk.test:8000/helpdesk` in your browser, you should see the app running


**For Frontend Development**
1. Open a new terminal session and cd into `frappe-bench/apps/helpdesk/desk`, and run the following commands:
    ```
    yarn install
    yarn dev or yarn dev --host helpdesk.test
    ```
1. Now, you can access the site on vite dev server at `http://helpdesk.test:8080`

**Note:** You'll find all the code related to Helpdesk's frontend inside `frappe-bench/apps/helpdesk/desk`

## Learn and connect

- [Telegram contact me ](https://t.me/robisurasko)

<br>
<br>
<div align="center">
	<a href="https://frappe.io" target="_blank">
		<picture>
			<source media="(prefers-color-scheme: dark)" srcset="https://frappe.io/files/Frappe-white.png">
			<img src="https://frappe.io/files/Frappe-black.png" alt="Frappe Technologies" height="28"/>
		</picture>
	</a>
</div>


<h1>WHATS IS THE CUSTOMIZATION AND UPDATE</h1>

1. Helpdesk Agent status
Status with Online, Busy and Offline base on HD Agent
Need to add manually the following step

- Edit Form HD Agent and create 2 fields
* Label = Curren Status, Name of Field = custom_current_status (Select) with 3 option Online, Busy and Offline (Default = Offline)
-> Purpooses : to log the status of Agent

* Label = Last Assignment, Name of Field = custom_last_assigment (Datetime)
-> Purposes : to check and automation of assigment with round robin

2. Auto assigment base on ONLY Agent with status ONLINE
Create Scheduler Event on SERVER SCRIPT with CRON and add the following script:
---
from helpdesk.helpdesk.doctype.ticket_assignment import assign_unassigned_tickets_round_robin

assign_unassigned_tickets_round_robin()
---