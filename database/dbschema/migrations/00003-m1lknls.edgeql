CREATE MIGRATION m1lknlsftjp3xma52el72hjqm7xnc4km2rzhywnf3fdnkbwggnaxtq
    ONTO m1ldht2jkqgvg4wvkdxpmcklrjnyg2wfg3ijvnpevcov45y562f6cq
{
  ALTER TYPE default::Photo {
      DROP PROPERTY file_data;
  };
  ALTER TYPE default::Photo {
      CREATE REQUIRED PROPERTY file_data_base64: std::str {
          SET REQUIRED USING (<std::str>{});
      };
  };
};
