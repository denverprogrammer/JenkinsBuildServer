/* Adds a multibranch pipeline job to jenkins
The internet doesn't seem to like this approach. Apparently I should use the DSL plugin.
The Jenkins internal API is what we are using here, and it works just fine except docs
are hard to come by.

I manually configured the job as I wanted, then ran: 

java -jar jenkins-cli.jar -auth admin:secret -s https://localhost:8443/ -noCertificateCheck get-job Cloudy-cron > /tmp/Cloudy-cron.xml

The output of that is used to work out what Java stuff I needed to create here.
*/

import hudson.util.PersistedList
import jenkins.model.Jenkins
import jenkins.branch.*
import jenkins.plugins.git.*
import org.jenkinsci.plugins.workflow.multibranch.*
import com.cloudbees.hudson.plugins.folder.*

// Bring some values in from environment.
String folderName = "Builds"
String jobName = "Symfony Docker"
String jobScript = "Jenkinsfile"
String gitRepo = "https://github.com/denverprogrammer/SymfonyDocker.git"
String credentialsId = "github-user"

Jenkins jenkins = Jenkins.instance // saves some typing

// Get the folder where this job should be
def folder = jenkins.getItem(folderName)

// Create the folder if it doesn't exist
if (folder == null) {
  folder = jenkins.createProject(Folder.class, folderName)
}

// Multibranch creation/update
WorkflowMultiBranchProject mbp
hudson.model.Item item = folder.getItem(jobName)

if ( item != null ) {
  // Update case
  mbp = (WorkflowMultiBranchProject) item
} else {
  // Create case
  mbp = folder.createProject(WorkflowMultiBranchProject.class, jobName)
}

// Configure the script this MBP uses
mbp.getProjectFactory().setScriptPath(jobScript)

// Add git repo
GitSCMSource gitSCMSource = new GitSCMSource(null, gitRepo, credentialsId, "*","", false)
BranchSource branchSource = new BranchSource(gitSCMSource)

// Remove and replace?
PersistedList sources = mbp.getSourcesList()
sources.clear()
sources.add(branchSource)
