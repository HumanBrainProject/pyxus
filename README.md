# Pyxus
Pyxus is a python library for accessing and managing the nexus knowledge graph.

##Concept
The access to nexus is provided through the *NexusClient* class. This class contains repositories for all structures provided by nexus (currently *contexts*, 
*domains*, *organizations*, *schemas* and *instances*). For all of these, the *NexusClient* provides repositories for easy access and manipulation:

###Repositories
Every repository provides similar functionalities:

* **create**: the creation of an entitiy
* **read**: the reading of an entity by its identifier
* **update**: the update of an entity
* **delete**: the deletion of an entity
* **listing/filtering**: the listing of entities (with parameters for filtering, resolution, pagination, etc.)

###Entities
There is an entity class for every type supported by pyxus (*Context*, *Domain*, *Organization*, *Schema*, *Instance*).
Entities are wrappers for the datastructures of Nexus and provide several convenience methods like **checksum calculation**, **full_qualification / expansion** as well as convenient accessor functions (e.g. for *revision*, *schema:identifier*, *publication state*, *deprecation state*)

The data structure provided by nexus results in *dict* constructs. which are accessible through
the **get_data** function.


###Search results
Additionally to the entities representing the different data structures in Nexus, Pyxus has some helper objects for search:

**SearchResultList** is the object returned by a listing / search. It contains aggregation values (*total*) as well as the results and accessor functions for pagination (*get_next_link*, *get_previous_link*). The result objects can either be **SearchResult** or an entity depending on the *resolve* parameter: If a search is executed with ```resolved=False```, Nexus only provides links to the actual entity. In this case, a *SearchResult* is returned which can be lazily by the *resolve* function of the repository. If ```resolved=True```, the resulting entities are already fully expanded and therefore returned in their wrapper objects.


##DataUploadUtils
Next to the access to the nexus structure through repositories, Pyxus provides 
utility functionality to manage the upload process to Nexus (*DataUploadutils*). 
This includes the possibility to upload predefined/precalculated JSON-LD structures stored in the local file system.

###Conventions
The upload of elements to nexus requires the following conventions:
The expected file path follows either the structure:
```{organization}/{domain}/{schema}/*{version}*.json```
or  
```{organization}/{domain}/{schema}/{version}/*.json```
where ```version``` fulfills the pattern ```vX.X.X```.

#### Instances
To make sure, that instances are updated instead of created by new in multiple uploads,
Pyxus checks for a ```http://schema.org/identifier```. If such an identifier can be found and already exists on Nexus, a new revision is created.


###Diff upload
To make sure the upload process is as efficient as possible, Pyxus calculates a hashcode of the uploaded file and stores it next to the file (a *.chksum file). 
Before uploading, Pyxus recalculates the checksum, compares it with the already existing file and if the checksum is equal, skips the upload.
To remove all checksums and therefore to enforce an upload, the *DataUploadUtils* provide a *clear_all_checksum* function.


###Resolution of linked data
Due to the fact that ids of instances are controlled by nexus, the linkage of data instances is difficult.
The *DataUploadUtils* provide a resolver functionality for this issue:

To define a link to another instance, you can define the following placeholder in your instance definition file:

```
"pyxus:my_relation": [
        "{{resolve /pyxus/core/related_instance/v0.0.1/?filter={\"filter\": {\"path\": \"http://schema.org/identifier\", \"value\": \"related_instance_identifier\", \"op\": \"eq\"}}}}"
]
```
With the resolve directive, the upload script tries to resolve the given nexus path and applies the found id. Any filter is possible - but it's important,
that the result set is non-ambiguous (contains only one entry) - therefore it's highly recommended to resolve the related instance by 
something unique (like e.g. a schema:identifier).

