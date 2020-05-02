// Harden Jenkins and remove all the nagging warnings in the web interface
import jenkins.model.Jenkins
import jenkins.security.s2m.*

Jenkins jenkins = Jenkins.getInstance()

// Disable remoting
jenkins.instance.setNumExecutors(1)
jenkins.getDescriptor("jenkins.CLI").get().setEnabled(false)
jenkins.setSlaveAgentPort(5000);

// Disable old Non-Encrypted protocols
HashSet<String> newProtocols = new HashSet<>(jenkins.getAgentProtocols());

newProtocols.removeAll(Arrays.asList("JNLP4-connect"));
jenkins.setAgentProtocols(newProtocols);
jenkins.save()
