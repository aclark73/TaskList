var sqlite = require("sqlite3");
var orm = require("orm");

orm.connect("sqlite://task_list.db", function (err, db) {
  if (err) throw err;

  var Task = db.define('task', {
	id: { type: "serial" },
	project: String,
	title: String,
	source: String,
	issue_id: String
  }, {
	methods: {
	  isProject: function() {
		return !this.title;
	  },
	  getUID: function() {
		if (this.isProject()) {
            return "P." + this.project;
        }
		else if (this.issue_id) {
            return "T." + this.source + "." + this.issue_id;
        }
		else {
		  return "T." + this.source + "." + this.project + "." + this.title;
		}
	  },
	  validations: {
		
	  }
	}
  });
  // add the table to the database 
  db.sync(function(err) { 
	if (err) throw err;
  });
  
  exports.Task = Task;
});
