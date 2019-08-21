var cScriptLoader = (function () {
    function cScriptLoader(files) {
      var _this = this;
      this.log = function (t) {
        console.log("NewApp: " + t);
      };
      this.withNoCache = function (filename) {
        if (filename.indexOf("?") === -1)
          filename += "?no_cache=" + new Date().getTime();
        else
          filename += "&no_cache=" + new Date().getTime();
        return filename;
      };
      this.loadStyle = function (filename) {
        // HTMLLinkElement
        var link = document.createElement("link");
        link.rel = "stylesheet";
        link.type = "text/css";
        link.href = filename;
        _this.log('Loading style ' + filename);
        link.onload = function () {
          _this.log('Loaded style "' + filename + '".');
        };
        link.onerror = function () {
          _this.log('Error loading style "' + filename + '".');
        };
        _this.m_head.appendChild(link);
      };
      this.loadScript = function (i) {
        var script = document.createElement('script');
        script.type = 'text/javascript';
        script.src = (_this.m_js_files[i]);
        var loadNextScript = function () {
          if (i + 1 < _this.m_js_files.length) {
            _this.loadScript(i + 1);
          }
        };
        script.onload = function () {
          _this.log('Loaded script "' + _this.m_js_files[i] + '".');
          loadNextScript();
        };
        script.onerror = function () {
          _this.log('Error loading script "' + _this.m_js_files[i] + '".');
          loadNextScript();
        };
        _this.log('Loading script "' + _this.m_js_files[i] + '".');
        _this.m_head.appendChild(script);
      };
      this.loadFiles = function () {
        // this.log(this.m_css_files);
        // this.log(this.m_js_files);
        for (var i = 0; i < _this.m_css_files.length; ++i)
          _this.loadStyle(_this.m_css_files[i]);
        _this.loadScript(0);
      };
      this.m_js_files = [];
      this.m_css_files = [];
      this.m_head = document.getElementsByTagName("head")[0];
      // this.m_head = document.head; // IE9+ only
      function endsWith(str, suffix) {
        if (str === null || suffix === null)
          return false;
        return str.indexOf(suffix, str.length - suffix.length) !== -1;
      }
      for (var i = 0; i < files.length; ++i) {
        if (endsWith(files[i], ".css")) {
          this.m_css_files.push(files[i]);
        } else if (endsWith(files[i], ".js")) {
          this.m_js_files.push(files[i]);
        } else
          this.log('Error unknown filetype "' + files[i] + '".');
      }
    }
    return cScriptLoader;
})();

var LoadScripts = new cScriptLoader([
    "https://cdn.quilljs.com/1.3.6/quill.snow.css",
    //"https://use.fontawesome.com/releases/v5.8.2/css/all.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.9.0/css/all.css",
    "https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datepicker/1.8.0/css/bootstrap-datepicker.min.css",
    "https://bootswatch.com/4/flatly/bootstrap.css",
    "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.8/styles/default.min.css",
    "https://code.jquery.com/jquery-3.3.1.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datepicker/1.8.0/js/bootstrap-datepicker.min.js",
    "https://cdn.quilljs.com/1.3.6/quill.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/socket.io/2.2.0/socket.io.js",
    "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js",
    "https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js",
    "https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.8/highlight.min.js",
    
]);

var LoadScriptsAdmin = new cScriptLoader([
  "https://use.fontawesome.com/releases/v5.0.6/css/all.css",
  "https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css",
  "https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css",
  "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.3.1/jquery.min.js",
  "https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js",
  "https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js",
  "https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"
]);
