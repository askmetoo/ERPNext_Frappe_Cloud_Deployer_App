## Deployer

Deploys the app changes into a specified instance


#### Usage
First install the app

To execute:

bench --site <site_name> execute deployer.deploy.startDeployment --kwargs "{'server':'<"server-name">', 'user':'<"user-name">', 'password':'<"password">'}"

    Example
    
    
        bench --site site1.local execute deployer.deploy.startDeployment --kwargs "{'server':'http://localhost:8080', 'user':'Administrator', 'password':'admin'}"


#### License

MIT
