var ResultModel = function(data) {
    var self = this;
    self.country = ko.observable(data["country"]);
    self.purpose = ko.observable(data["purpose"]);
    self.signing_authority_defaulttext = ko.observable(data["signing_authority_defaulttext"]);
    self.url = ko.observable(data["url"]);
    self.clickableUrl = ko.computed(() => {
        return "/api/document?url="+ encodeURIComponent(self.url());
    });
}

var MainModel = function() {
    var self = this;
    self.countries = ko.observableArray([]);
    self.selectedCountry = ko.observable();
    self.purposes = ko.observableArray([]);
    self.selectedPurpose = ko.observable();    
    self.eid = ko.observable("12345678901@id.bund.de");

    self.results = ko.observableArray([]);

    self.setSampleeIDCZ = function() {
        self.eid("12345840761@identitaobcana.cz");
    }

    self.setSampleeIDDE = function() {
        self.eid("12345678901@id.bund.de");
    }

    self.refreshCountries = function() {
        fetch("/api/countries")
            .then(response => response.json())
            .then(json => {
                var mapped_json = [];
                for (var e in json) {
                    mapped_json.push({
                        "key": e,
                        "value": json[e]
                    });
                }
                self.countries(mapped_json)
            });
    }

    self.refreshPurposes = function() {
        fetch("/api/purposes")
            .then(response => response.json())
            .then(json => {
                var mapped_json = [];
                for (var e in json) {
                    mapped_json.push({
                        "key": e,
                        "value": json[e]
                    });
                }
                self.purposes(mapped_json)
            });            
    }

    self.searchDocuments = function() {
        var url = "/api/find/"
            + self.selectedCountry() + "/" 
            + self.selectedPurpose() + "/" 
            + self.eid();

        fetch(url)
            .then(response => response.json())
            .then(json => {
                var mapped_json = [];
                for (var idx = 0; idx < json.length; idx++) {
                    mapped_json.push(new ResultModel(json[idx]));
                }
                self.results(mapped_json);
            });
    }

    // initialize countries and purposes
    self.refreshCountries();
    self.refreshPurposes();
}

var m = new MainModel();
ko.applyBindings(m);