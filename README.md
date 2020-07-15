## Deployer

Deploys the app changes into a specified instance


#### Usage
1. Define what all needs to be exported from your app inside fixtures in hooks.py file.
2. Run the below command to export the fixtures-
   
   bench --site <site-name> export-fixtures

3. Now install the deployer app and execute the given command as below given format-

    bench --site <site_name> execute deployer.deploy.startDeployment --kwargs "{'server':'<"server-name">', 'user':'<"user-name">', 'password':'<"password">','key':'<"api_key'>'}"

    Example
    
        bench --site site1.local execute deployer.deploy.startDeployment --kwargs "{'server':'http://localhost:8080', 'user':'Administrator', 'password':'admin','key':'9e9ef49c13207e2'}"


#### License

MIT
