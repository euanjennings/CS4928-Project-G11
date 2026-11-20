package brut.androlib.res;

import brut.androlib.Config;
import brut.androlib.exceptions.AndrolibException;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TemporaryFolder;

import java.io.File;
import java.nio.file.Files;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertThrows;

/** Event B retrospective follow-up: the four original tests plus a failure-path test. */
public class FrameworkCacheSummaryTest {

    @Rule
    public TemporaryFolder temp = new TemporaryFolder();

    private Framework create(String frameworkDirectory) {
        Config config = Config.getDefaultConfig();
        config.frameworkDirectory = frameworkDirectory;
        return new Framework(config);
    }

    private Framework create() {
        return create(temp.getRoot().getAbsolutePath());
    }

    @Test
    public void emptyDirectory() throws Exception {
        assertEquals("0 APK files, 0 bytes", create().getFrameworkCacheSummary());
    }

    @Test
    public void countsApkFilesAndSizes() throws Exception {
        Files.write(temp.newFile("1.apk").toPath(), new byte[100]);
        Files.write(temp.newFile("2-vendor.apk").toPath(), new byte[250]);

        assertEquals("2 APK files, 350 bytes", create().getFrameworkCacheSummary());
    }

    @Test
    public void ignoresNonApkFiles() throws Exception {
        Files.write(temp.newFile("1.apk").toPath(), new byte[100]);
        Files.write(temp.newFile("notes.txt").toPath(), new byte[20]);

        assertEquals("1 APK files, 100 bytes", create().getFrameworkCacheSummary());
    }

    @Test
    public void ignoresDirectoriesNamedApk() throws Exception {
        temp.newFolder("fake.apk");

        assertEquals("0 APK files, 0 bytes", create().getFrameworkCacheSummary());
    }

    @Test
    public void rejectsFramePathThatIsAFile() throws Exception {
        File notADirectory = temp.newFile("frame-path.txt");

        assertThrows(AndrolibException.class,
                () -> create(notADirectory.getAbsolutePath()).getFrameworkCacheSummary());
    }
}
