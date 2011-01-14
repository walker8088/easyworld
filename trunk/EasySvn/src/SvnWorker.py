
import time
import pysvn

class RepoInfo() :
    def __init__(self, work_path, server_url = None, user = None, passwd = None, last_rev = 0):
        self.work_path = work_path
        self.server_url = server_url
        self.user = user
        self.passwd = passwd
        self.last_rev = last_rev 	

def callback_ssl_server_trust_prompt( trust_data ):
            return True, trust_data['failures'], True
        
class SvnWorker :
        def __init__(self, repo) :
            self.repo = repo
            self.client = pysvn.Client()
           
            self.client.callback_get_login = self.callback_get_login
            self.client.callback_ssl_server_trust_prompt = callback_ssl_server_trust_prompt 
        
        
        def getCurrLocalRevNo(self) :        
                entry = self.client.info(self.repo.work_path)
                return entry.revision.number
        
        def getCurrRepoRevNo(self) :
            work_path = self.repo.work_path
            entry = self.client.info(work_path)
            old_rev = entry.revision.number
            repos = entry.repos
                
            log = self.client.log(repos, 
                             revision_end=pysvn.Revision( pysvn.opt_revision_kind.number, old_rev), 
                             limit = 1
                    )
                    
            return log[0].revision.number
            
        def callback_get_login(realm, username, may_save):
                """Return the default login credentials"""
                print "here"
                return True, self.repo.user, self.repo.passwd, False
        
        def update(self) :
                work_path = self.repo.work_path
                
                entry = self.client.info(work_path)
                old_rev = entry.revision.number
                revs = self.client.update(work_path)
                new_rev = revs[-1].number
                print 'updated from %s to %s.\n' % (old_rev, new_rev)

                head = pysvn.Revision(pysvn.opt_revision_kind.number, old_rev)
                end = pysvn.Revision(pysvn.opt_revision_kind.number, new_rev)

                log_messages = self.client.log(work_path, revision_start=head, revision_end=end,
                        limit=0)
                for log in log_messages:
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(log.date))
                    print '[%s]\t%s\t%s\n  %s\n' % (log.revision.number, timestamp,
                            log.author, log.message)
                print

                FILE_CHANGE_INFO = {
                        pysvn.diff_summarize_kind.normal: ' ',
                        pysvn.diff_summarize_kind.modified: 'M',
                        pysvn.diff_summarize_kind.delete: 'D',
                        pysvn.diff_summarize_kind.added: 'A',
                        }

                print 'file changed:'
                summary = self.client.diff_summarize(work_path, head, work_path, end)
                for info in summary:
                    path = info.path
                    if info.node_kind == pysvn.node_kind.dir:
                        path += '/'
                    file_changed = FILE_CHANGE_INFO[info.summarize_kind]
                    prop_changed = ' '
                    if info.prop_changed:
                        prop_changed = 'M'
                    print file_changed + prop_changed, path
                print

        def discover_changes(client, rev_number):
            revision_min =pysvn.Revision(pysvn.opt_revision_kind.number,rev_number-1)
            revision_max = pysvn.Revision(pysvn.opt_revision_kind.number, rev_number)

            log = client.log(
                #repo_dict[curr_repo].server, 
                "file://" + repo_dict[curr_repo].work_path,
                revision_max, revision_min, 
                discover_changed_paths=True,
                )

            if len(log) is 1:
                return [], []

            authors = []
            paths = []
            dict = {"A":"Add", "M":"Modify", "D":"Delete"}
            for entry in log[:-1]:
                if entry.author not in authors:
                    authors.append(entry.author)
                for change in entry.changed_paths:
                    try :	
                        path = change.path.decode("utf-8")
                    except :
                        path = change.path
                    action = dict[change.action]
                    paths.append(("[%s] %s") % (action, path))
            
            last_revision = log[0].revision
                
            return log[0].message, paths, authors

