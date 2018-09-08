var http = require('http'),
    httpProxy = require('http-proxy');
    url = require('url');

var workshop_app = 'http://127.0.0.1:8081';
var terminal_app = 'http://127.0.0.1:8082';

var terminal_top = process.env.URI_ROOT_PATH || '/user/default'
var terminal_url = '^' + terminal_top + '/terminal/.*$';

var terminal_user = process.env.TERMINAL_USER
var terminal_pass = process.env.TERMINAL_PASS

console.log('TERMINAL_URL' + terminal_url);

var proxy = httpProxy.createProxyServer({});

function on_error(err, req, res) {
  res.writeHead(500, {
    'Content-Type': 'text/plain'
  });

  res.end('Something went wrong.');
}

var server = http.createServer(function(req, res) {
  var auth = req.headers['authorization'];

  if (terminal_user) {
    if (!auth) {
	res.statusCode = 401;
	res.setHeader('WWW-Authenticate', 'Basic realm="Terminal"');

	res.end('Login required.');
    }
    else {
      var tmp = auth.split(' ');
      var buf = new Buffer(tmp[1], 'base64');
      var plain_auth = buf.toString();

      var creds = plain_auth.split(':');
      var username = creds[0];
      var password = creds[1];

      if ((username != terminal_user) || (password != terminal_pass)) {
	res.statusCode = 401;
	res.setHeader('WWW-Authenticate', 'Basic realm="Terminal"');

	res.end('Access denied.');
      }
    }
  }

  var target_app = workshop_app;

  var parsed_url = url.parse(req.url);

  if (parsed_url.pathname.match(terminal_url))
      target_app = terminal_app;

  proxy.web(req, res, { target: target_app }, on_error);
});

server.on('upgrade', function (req, socket, head) {
  var target_app = workshop_app;

  var parsed_url = url.parse(req.url);

  if (parsed_url.pathname.match(terminal_url))
      target_app = terminal_app;

  proxy.ws(req, socket, head, { target: target_app }, on_error);
});

server.listen(8080, "0.0.0.0");
