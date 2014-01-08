import os, sys, hashlib, urllib2, tempfile, zipfile, distutils.core


class JMeterInstaller(object):

    def __init__(self):
        self.jmeter_version = "2.11"
        self.jmeter_dir = "apache-jmeter-%s/" % self.jmeter_version
        self.download_dir = tempfile.mkdtemp()
        self.md5map = {"jmeter.zip": "14b6dfc04f912e45b482e4563fdf1c3a",
                       "jmp-standard.zip": "bee82c91e06d9eee81bf61618e48066e",
                       "jmp-extras.zip": "f908b5699a9f30e0745740ca11db4ef7",
                       "jmp-extraslibs.zip": "ec2e43400f13de1b2e68d05e7721ac4a"}

    def clean(self):
        if os.path.exists(self.download_dir):
            print("Removing %s" % self.download_dir)
            distutils.dir_util.remove_tree(self.download_dir)

    def get_file(self, url, local_path):
        print("Downloading " + url)
        stream = urllib2.urlopen(url)
        with(open(self.download_dir + local_path, "wb")) as f:
            f.write(stream.read())

        with(open(f.name, "rb")) as written:
            md5 = hashlib.md5(written.read()).hexdigest()
            if self.md5map[local_path] != md5:
                self.clean()
                raise Exception("MD5 mismatch. Expected %s but received %s" % (self.md5map[local_path], md5))



    def unzip_plugin(self, zip_file, to_dir):
        out = self.jmeter_dir + to_dir
        with(zipfile.ZipFile(self.download_dir + zip_file, "r")) as z:
            z.extractall(out)
            distutils.dir_util.copy_tree(out + "/lib", self.jmeter_dir + "/lib")
            distutils.dir_util.remove_tree(out + "/lib")
        print("JMeter Plugin copied to JMeter lib directory. README for the plugin available at %s%s" % (self.jmeter_dir, to_dir))


    def install_jmeter(self):
        if not os.path.exists(self.jmeter_dir):
            print("Download JMeter")

            jmeter_file = "http://apache.mirrors.tds.net/jmeter/binaries/apache-jmeter-%s.zip" % self.jmeter_version
            self.get_file(jmeter_file, "jmeter.zip")

            with(zipfile.ZipFile(self.download_dir + "jmeter.zip", "r")) as z:
                z.extractall()

            os.chmod(self.jmeter_dir + "/bin/jmeter.sh", 0755)
        else:
            print("JMeter directory [%s] exists... skipping" % self.jmeter_dir)

    def install_plugins(self):
        print("Installing JMeter Plugins")

        base_url = 'http://jmeter-plugins.org/downloads/file/'
        plugins = [['JMeterPlugins-Standard', '1.1.2', 'jmp-standard'],
                   ['JMeterPlugins-Extras', '1.1.2', 'jmp-extras'],
                   ['JMeterPlugins-ExtrasLibs', '1.1.2', 'jmp-extraslibs']]

        for plugin in plugins:
            if not os.path.exists(self.jmeter_dir + "lib/ext/" + plugin[0] + ".jar"):
                self.get_file(base_url + plugin[0] + "-" + plugin[1] + ".zip", plugin[2] + ".zip")

                self.unzip_plugin(plugin[2] + ".zip", plugin[2])
            else:
                print("%s appear to exist in %slib/ext" % (plugin[0], self.jmeter_dir))

    def install(self):
        try:
            self.install_jmeter()
            self.install_plugins()
            self.clean()
            return os.path.exists(self.jmeter_dir)
        except:
            self.clean()
            print "Unexpected error:", sys.exc_info()
            raise


if __name__ == '__main__':
    jmi = JMeterInstaller()
    res = jmi.install()
    print("Does jmeter install path %s exist? %s" % (jmi.jmeter_dir, res))