from rassh.managers.bonaire_ssh_commands import BonaireSSHCommands
from rassh.config.postgres_config import PostgresConfig

postgres_config_instance = PostgresConfig()
postgres_config = postgres_config_instance.data
my_database_user = postgres_config['postgres_user']

commands = BonaireSSHCommands(None)

object_types = set()

print("""CREATE TABLE ssh_api_status (status VARCHAR (1024), time_checked TIMESTAMP(0) WITH TIME ZONE);""")
print("")
print("GRANT ALL ON ssh_api_status TO " + my_database_user + ";")
print("")

if commands.grammar.parameters:
    for command_name, command_options in commands.grammar.parameters.items():
        object_types.add(command_options['object_type'])

    for table_name in object_types:
        if table_name == "status":
            continue
        key_name = commands.grammar.object_type_to_key_name[table_name]

        print("""CREATE TABLE latest_""" + table_name + """_config_results (
                 """ + key_name + """ VARCHAR (32) PRIMARY KEY,
                 response VARCHAR (255) NOT NULL,
                 status SMALLINT NOT NULL,
                 last_updated timestamp(0) with time zone NOT NULL,
                 CONSTRAINT latest_""" + table_name + "_config_results_" + key_name + "_fkey FOREIGN KEY ("
              + key_name + ") REFERENCES " + table_name +"s (" + key_name + ") MATCH SIMPLE ON UPDATE CASCADE "
              + "ON DELETE CASCADE" + """
                 );""")
        print("")
        print("GRANT ALL ON latest_" + table_name + "_config_results TO " + my_database_user + ";")
        print("")

        # We don't want a foreign key constraint here, because we want to keep logs after the parent object has been
        # deleted, for example.
        print("""CREATE TABLE logged_config_""" + table_name + """s (
                 id BIGSERIAL PRIMARY KEY,
                 """ + key_name + """ VARCHAR (32),
                 command VARCHAR (255),
                 response VARCHAR (255) NOT NULL,
                 status SMALLINT NOT NULL,
                 time_completed timestamp(0) with time zone NOT NULL);""")
        print("")
        print("GRANT ALL ON logged_config_" + table_name + "s TO " + my_database_user + ";")
        print("GRANT USAGE, SELECT ON SEQUENCE logged_config_" + table_name + "s_id_seq TO " + my_database_user + ";")
        print("")

        print("""CREATE TABLE outstanding_config_""" + table_name + """s (
                 """ + key_name + """ VARCHAR (32) PRIMARY KEY,
                 command VARCHAR (255) NOT NULL,
                 time_requested timestamp(0) with time zone NOT NULL,
                 sent BOOLEAN NOT NULL,
                 time_sent timestamp(0) with time zone,
                 CONSTRAINT outstanding_config_""" + table_name + "_config_results_" + key_name + "_fkey FOREIGN KEY ("
              + key_name + ") REFERENCES " + table_name +"s (" + key_name + ") MATCH SIMPLE ON UPDATE CASCADE "
              + "ON DELETE CASCADE" + """
                 );""")
        print("")
        print ("GRANT ALL ON outstanding_config_" + table_name + "s TO " + my_database_user + ";")
        print("")

else:
    print("No commands found!")
