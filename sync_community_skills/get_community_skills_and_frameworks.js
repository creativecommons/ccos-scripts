const express = require('express');
const app = express();
const axios = require('axios')
const fs = require('fs');
app.use(express.json());

const result = [];
const jsonObject = {
        name: "",
        languages: {}   
};

axios.get('https://api.github.com/orgs/creativecommons/repos').then((obj) => {
    const data = obj.data;
    for(const property in data){
        // console.log("Hello World")
        axios.get(data[property].languages_url).then(async (obj) => {
            jsonObject.name=data[property].name
            jsonObject.languages = obj.data
            console.log(jsonObject)
        })
    }

}
)
const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Listening on port ${port}`));