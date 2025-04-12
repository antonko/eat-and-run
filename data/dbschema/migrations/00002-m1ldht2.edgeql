CREATE MIGRATION m1ldht2jkqgvg4wvkdxpmcklrjnyg2wfg3ijvnpevcov45y562f6cq
    ONTO m1ekowga2x2gzocojbs2rrvbtggcelntmc7uua5j3jrccng7bckkoq
{
  CREATE SCALAR TYPE default::PhotoNumber EXTENDING std::sequence;
  ALTER TYPE default::Photo {
      CREATE REQUIRED PROPERTY id_int: default::PhotoNumber {
          SET REQUIRED USING (<default::PhotoNumber>{});
          CREATE CONSTRAINT std::exclusive;
      };
  };
};
