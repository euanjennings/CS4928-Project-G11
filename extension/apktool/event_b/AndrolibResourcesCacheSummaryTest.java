package brut.androlib.res;

import brut.androlib.Config;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TemporaryFolder;

import java.nio.file.Files;

import static org.junit.Assert.assertEquals;

public class AndrolibResourcesCacheSummaryTest {

    @Rule
    public TemporaryFolder temp = new TemporaryFolder();

    private AndrolibResources createResources() {
        Config config = Config.getDefaultConfig();
        config.frameworkDirectory = temp.getRoot().getAbsolutePath();
        return new AndrolibResources(config);
    }

    @Test
    public void emptyDirectory() throws Exception {
        assertEquals("0 APK files, 0 bytes",
                createResources().getFrameworkCacheSummary());
    }

    @Test
    public void countsApkFilesAndSizes() throws Exception {
        Files.write(temp.newFile("1.apk").toPath(), new byte[100]);
        Files.write(temp.newFile("2-vendor.apk").toPath(), new byte[250]);

        assertEquals("2 APK files, 350 bytes",
                createResources().getFrameworkCacheSummary());
    }

    @Test
    public void ignoresNonApkFiles() throws Exception {
        Files.write(temp.newFile("1.apk").toPath(), new byte[100]);
        Files.write(temp.newFile("notes.txt").toPath(), new byte[20]);

        assertEquals("1 APK files, 100 bytes",
                createResources().getFrameworkCacheSummary());
    }

    @Test
    public void ignoresDirectoriesNamedApk() throws Exception {
        temp.newFolder("fake.apk");

        assertEquals("0 APK files, 0 bytes",
                createResources().getFrameworkCacheSummary());
    }
}