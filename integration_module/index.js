const express = require('express');
const app = express();
const router = express.Router();
const port = 9076;

app.use(express.json());

// url: http://localhost:3000/
app.get('/', (request, response) => response.send('Hello World'));

// all routes prefixed with /api
app.use('/api', router);

// using router.get() to prefix our path
// url: http://localhost:3000/api/
router.get('/', (request, response) => {
  response.json({message: 'Hello, welcome to my server'});
});

app.post('/test', (request, response) => {
  console.log("request", request.body)
  response.json({dob: '1st April', customer_name: 'Fool Customer'});
});


// set the server to listen on port 3000
app.listen(port, () => console.log(`Listening on port ${port}`));
