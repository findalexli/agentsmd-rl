import org.openqa.selenium.Keys;
import java.lang.reflect.Field;

public class TestKeysHarness {
    public static void main(String[] args) throws Exception {
        if (args.length != 1) {
            throw new RuntimeException("Usage: TestKeysHarness <test_name>");
        }
        String which = args[0];
        switch (which) {
            case "option_charat_equals_alt":
                check(Keys.OPTION.charAt(0) == Keys.ALT.charAt(0),
                    "OPTION.charAt(0) (=" + hex(Keys.OPTION.charAt(0)) + ") != ALT.charAt(0) (=" + hex(Keys.ALT.charAt(0)) + ")");
                break;
            case "option_unicode_e00a":
                check(Keys.OPTION.charAt(0) == 0xE00A,
                    "OPTION expected \\uE00A but was " + hex(Keys.OPTION.charAt(0)));
                break;
            case "option_codepoint_equals_alt":
                check(Keys.OPTION.getCodePoint() == Keys.ALT.getCodePoint(),
                    "OPTION codepoint (" + Integer.toHexString(Keys.OPTION.getCodePoint()) + ") != ALT codepoint (" + Integer.toHexString(Keys.ALT.getCodePoint()) + ")");
                break;
            case "option_tostring_equals_alt":
                check(Keys.OPTION.toString().equals(Keys.ALT.toString()),
                    "OPTION.toString() != ALT.toString()");
                break;
            case "fn_is_deprecated":
                Field fn = Keys.class.getField("FN");
                check(fn.isAnnotationPresent(Deprecated.class),
                    "Keys.FN must be annotated with @Deprecated");
                break;
            case "right_alt_unicode":
                check(Keys.RIGHT_ALT.charAt(0) == 0xE052,
                    "RIGHT_ALT must remain \\uE052 (was " + hex(Keys.RIGHT_ALT.charAt(0)) + ")");
                break;
            case "right_control_unicode":
                check(Keys.RIGHT_CONTROL.charAt(0) == 0xE051,
                    "RIGHT_CONTROL must remain \\uE051 (was " + hex(Keys.RIGHT_CONTROL.charAt(0)) + ")");
                break;
            case "alt_unicode":
                check(Keys.ALT.charAt(0) == 0xE00A,
                    "ALT must remain \\uE00A (was " + hex(Keys.ALT.charAt(0)) + ")");
                break;
            case "fn_charat_equals_right_control":
                check(Keys.FN.charAt(0) == Keys.RIGHT_CONTROL.charAt(0),
                    "FN.charAt(0) != RIGHT_CONTROL.charAt(0)");
                break;
            case "option_field_exists":
                Keys.class.getField("OPTION");
                break;
            case "fn_field_exists":
                Keys.class.getField("FN");
                break;
            case "right_alt_returned_for_e052":
                check(Keys.getKeyFromUnicode((char) 0xE052) == Keys.RIGHT_ALT,
                    "getKeyFromUnicode(0xE052) should return RIGHT_ALT");
                break;
            default:
                throw new RuntimeException("Unknown test: " + which);
        }
        System.out.println("OK");
    }

    static void check(boolean cond, String msg) {
        if (!cond) throw new AssertionError(msg);
    }

    static String hex(char c) {
        return "\\u" + String.format("%04X", (int) c);
    }
}
