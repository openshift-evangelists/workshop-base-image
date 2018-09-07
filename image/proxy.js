var http = require('http'),
    httpProxy = require('http-proxy');
    url = require('url');

var workshop_app = 'http://127.0.0.1:8081';
var terminal_app = 'http://127.0.0.1:8082';

var terminal_top = process.env.URI_ROOT_PATH || '/user/default'
var terminal_url = '^' + terminal_top + '/terminal/.*$';

console.log('TERMINAL_URL' + terminal_url);

var proxy = httpProxy.createProxyServer({});

function on_error(err, req, res) {
  res.writeHead(500, {
    'Content-Type': 'text/plain'
  });

  res.end('Something went wrong.');
}

var server = http.createServer(function(req, res) {
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
