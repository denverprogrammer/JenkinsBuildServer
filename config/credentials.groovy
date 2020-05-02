#!groovy

// imports
import com.cloudbees.plugins.credentials.*
import com.cloudbees.plugins.credentials.domains.Domain
import com.cloudbees.plugins.credentials.impl.*
import hudson.util.Secret
import jenkins.model.Jenkins

// get Jenkins instance
Jenkins jenkins = Jenkins.getInstance()

// get credentials store
def store = jenkins.getExtensionList('com.cloudbees.plugins.credentials.SystemCredentialsProvider')[0].getStore()

// define Bitbucket secret
def credentials = new UsernamePasswordCredentialsImpl(
  CredentialsScope.GLOBAL,
  'github-user',
  'Github username and api token',
  'denverprogrammer',
  '46db655ca3c21f2c8369810b3ffed81db670fd51'
)

// add credential to store
store.addCredentials(Domain.global(), credentials)

// save to disk
jenkins.save()
