

variable "amis" {
	 type = "map"
         description = "AMIs for the different pipeline node types"
         default = {
                 elasticsearch = "ami-fe6a5381"
		 couchbase = "ami-6c7cdb7a"	# couchbase community 4.5.0
                 redis = "ami-bcb93eab"		# bitnami redis on Ubuntu 14.04.3
                 postgres = "ami-12f6ba05"	# bitnami postgres 9.6 on Ubuntu 14.04.3
        } 
}


