import json
import re


class JSONLinter:
    @staticmethod
    def lint(text: str) -> dict:
        text = text.strip()
        if not text:
            return {"valid": False, "errors": [{"line": 1, "col": 1, "message": "Empty input"}], "formatted": ""}

        errors = []

        # Check for common issues before parsing
        errors.extend(JSONLinter._check_trailing_commas(text))
        errors.extend(JSONLinter._check_single_quotes(text))
        errors.extend(JSONLinter._check_unquoted_keys(text))

        # Try standard parse
        try:
            obj = json.loads(text)
            formatted = json.dumps(obj, indent=2, ensure_ascii=False)
            if errors:
                return {"valid": False, "errors": errors, "formatted": formatted}
            return {"valid": True, "errors": [], "formatted": formatted}
        except json.JSONDecodeError as e:
            errors.append({
                "line": e.lineno,
                "col": e.colno,
                "message": e.msg,
            })
            return {"valid": False, "errors": errors, "formatted": ""}

    @staticmethod
    def format_json(text: str) -> str:
        obj = json.loads(text)
        return json.dumps(obj, indent=2, ensure_ascii=False)

    @staticmethod
    def _check_trailing_commas(text: str) -> list:
        errors = []
        lines = text.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.rstrip()
            # Trailing comma before } or ]
            if re.search(r',\s*$', stripped):
                # Check if next non-empty line starts with } or ]
                for j in range(i, len(lines)):
                    next_line = lines[j].strip()
                    if next_line:
                        if next_line[0] in '}]':
                            errors.append({
                                "line": i,
                                "col": len(stripped),
                                "message": "Trailing comma before closing bracket",
                            })
                        break
        return errors

    @staticmethod
    def _check_single_quotes(text: str) -> list:
        errors = []
        in_string = False
        escape = False
        lines = text.split('\n')
        for i, line in enumerate(lines, 1):
            for j, ch in enumerate(line):
                if escape:
                    escape = False
                    continue
                if ch == '\\':
                    escape = True
                    continue
                if ch == '"':
                    in_string = not in_string
                elif ch == "'" and not in_string:
                    errors.append({
                        "line": i,
                        "col": j + 1,
                        "message": "Single quotes not allowed in JSON; use double quotes",
                    })
                    return errors  # Report first occurrence only
        return errors

    @staticmethod
    def _check_unquoted_keys(text: str) -> list:
        errors = []
        pattern = re.compile(r'(?<!["\w])(\b[a-zA-Z_]\w*)\s*:')
        lines = text.split('\n')
        for i, line in enumerate(lines, 1):
            # Skip if inside a string (simple heuristic)
            for m in pattern.finditer(line):
                # Check if the key is not inside quotes
                before = line[:m.start()]
                quote_count = before.count('"') - before.count('\\"')
                if quote_count % 2 == 0:
                    errors.append({
                        "line": i,
                        "col": m.start(1) + 1,
                        "message": f"Unquoted key '{m.group(1)}'; keys must be double-quoted",
                    })
                    return errors  # Report first only
        return errors
