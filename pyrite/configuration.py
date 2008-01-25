
import ConfigParser, os
import pyrite

class ConfigError(Exception):
    """Raised when unable to load config"""

class Config:
    def __init__(self):
        self.user_config_path = os.path.expanduser('~/.pytrc')
        self.user_config = ConfigParser.SafeConfigParser()
        self.user_config.readfp(self._get_file())
        if pyrite.repo.is_repo():
            self.repo_config_path = os.path.join(repo.get_repo_dir(), 'pytrc')
            self.repo_config = ConfigParser.SafeConfigParser()
            self.repo_config.readfp(self._get_file(True))
            
    def _get_file(self, is_global=True):
        rcpath = None
        if is_global:
            f = self.user_config_path
        else:
            f = self.repo_config_path
        try: return open(f, "r+")
        except IOError:
            try: return open(f, "w+")
            except: raise ConfigError("User config not available")

    def set_repo_option(self, category, name, value):
        if not repo.is_repo(): raise ConfigError("Not under a repository")
        self._set_option(self.repo_config, self.repo_config_name, category,
                            name, value)

    def set_user_option(self, category, name, value):
        self._set_option(self.user_config, self.user_config_name, category,
                            name, value)

    def del_repo_option(self, category, name):
        if not repo.is_repo(): raise ConfigError("Not under a repository")
        self._del_option(self.repo_config, self.repo_config_name, category,
                            name)

    def del_user_option(self, category, name):
        self._del_option(self.user_config, self.user_config_name, category,
                            name)

    def _del_option(self, config, file_obj, category, name):
        if category == None or name == None:
            raise ValueError("Category and Name must be supplied")
        if config.has_section(category):
            config.remove_option(category, name)
            if config.options(category).empty():
                config.remove_section(category)
            config.write(file_obj)

    def _set_option(self, config, file_obj, category, name, value):
        if category == None or name == None:
            raise ValueError("Category and Name must be supplied")
        if not config.has_section(category):
            config.add_section(category)
        config.set(category, option, value)
        config.write(file_obj)

    def get_option(self, category, name):
        if category == None or name == None:
            raise ValueError("Category and Name must be supplied")
        if self.repo_config.has_option(category, name):
            return self.repo_config.get(category, name)
        elif self.user_config.has_option(category, name):
            return self.user_config.get(category, name)
        else:
            return None

def run(options, remainder):
    is_user = True
    if options.has_key('repo'):
        is_user = False

    if options.has_key('set'):
        if len(remainder) != 3:
            raise HelpError()
        if is_user:
            config.set_user_option(remainder[0], remainder[1], remainder[2])
        else:
            config.set_repo_option(remainder[0], remainder[1], remainder[2])
    elif options.has_key('get'):
        if len(remainder) != 2:
            raise HelpError()
        value = None
        if is_user:
            value = config.get_user_option(remainder[0], remainder[1])
        else:
            value = config.set_repo_option(remainder[0], remainder[1])
        ui.info(value == None and '' or value)
    else:        
        raise HelpError("Need to set or get config option")


