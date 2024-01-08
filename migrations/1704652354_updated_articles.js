/// <reference path="../pb_data/types.d.ts" />
migrate(
  (db) => {
    const dao = new Dao(db);
    const collection = dao.findCollectionByNameOrId("y6rn1f1abvxdjbs");

    // remove
    collection.schema.removeField("l7sth1bt");

    // add
    collection.schema.addField(
      new SchemaField({
        system: false,
        id: "rqszxlk8",
        name: "embeddings_generated",
        type: "bool",
        required: false,
        presentable: false,
        unique: false,
        options: {},
      })
    );

    // add
    collection.schema.addField(
      new SchemaField({
        system: false,
        id: "l4sth1bt",
        name: "pdf_url",
        type: "text",
        required: false,
        presentable: false,
        unique: false,
        options: {
          min: null,
          max: null,
          pattern: "",
        },
      })
    );

    return dao.saveCollection(collection);
  },
  (db) => {
    const dao = new Dao(db);
    const collection = dao.findCollectionByNameOrId("y6rn1f1abvxdjbs");

    // add
    collection.schema.addField(
      new SchemaField({
        system: false,
        id: "l7sth1bt",
        name: "vector_id",
        type: "text",
        required: false,
        presentable: false,
        unique: false,
        options: {
          min: null,
          max: null,
          pattern: "",
        },
      })
    );

    // remove
    collection.schema.removeField("rqszxlk8");

    // remove
    collection.schema.removeField("l4sth1bt");

    return dao.saveCollection(collection);
  }
);
