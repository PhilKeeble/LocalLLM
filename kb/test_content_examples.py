"""Check constructed numeric examples, not target ABI/compiler behavior."""
import math
import struct
import unittest


class ContentExamples(unittest.TestCase):
    def test_constructed_jni_modified_utf8_capacity(self):
        # Encoding and finite-width allocation arithmetic, not JNI execution.
        lengths = [1 if 1 <= unit <= 0x7f else 2 if unit <= 0x7ff else 3
                   for unit in range(0x10000)]
        self.assertEqual(max(lengths), 3)
        self.assertEqual((lengths[0], lengths[0xd83d], lengths[0xde00]), (2, 3, 3))
        units = [0x41, 0, 0xd83d, 0xde00]
        actual = sum(lengths[unit] for unit in units)
        capacity = 3 * len(units) + 1
        self.assertEqual((actual, capacity), (9, 13))
        self.assertLessEqual(actual + 1, capacity)
        for max_capacity in (0x7fffffff, 0xffffffff):
            largest_count = (max_capacity - 1) // 3
            self.assertLessEqual(3 * largest_count + 1, max_capacity)
            self.assertGreater(3 * (largest_count + 1) + 1, max_capacity)

    def test_constructed_jvm_branch_switch_and_slots(self):
        # Encoding arithmetic only: no class-file verifier or JVM execution.
        branch = bytes.fromhex("A7 FF F8")
        self.assertEqual(12 + int.from_bytes(branch[1:], "big", signed=True), 4)
        bci = 5
        padding = (-(bci + 1)) % 4
        self.assertEqual(padding, 2)
        self.assertEqual(bci + 1 + padding, 8)
        low, high = 2, 3
        switch_end = bci + 1 + padding + 12 + (high - low + 1) * 4
        self.assertEqual(switch_end, 28)
        self.assertEqual(bci + int.from_bytes(bytes.fromhex("FF FF FF FB"),
                                            "big", signed=True), 0)
        widths = [1, 1, 2, 1]  # this, int, long, byte[] reference
        starts = [sum(widths[:n]) for n in range(len(widths))]
        self.assertEqual(starts, [0, 1, 2, 4])

    def test_constructed_jvm_modified_utf8_example(self):
        # Construct encoding from UTF-16 units; not a Java decoder conformance test.
        value = "A\x00\U0001f600"
        utf16 = value.encode("utf-16-be")
        units = [int.from_bytes(utf16[n:n + 2], "big")
                 for n in range(0, len(utf16), 2)]
        encoded = bytearray()
        for unit in units:
            if 1 <= unit <= 0x7f:
                encoded.append(unit)
            elif unit <= 0x7ff:
                encoded.extend([0xc0 | (unit >> 6), 0x80 | (unit & 0x3f)])
            else:
                encoded.extend([0xe0 | (unit >> 12),
                                0x80 | ((unit >> 6) & 0x3f),
                                0x80 | (unit & 0x3f)])
        self.assertEqual(bytes(encoded), bytes.fromhex("41 C0 80 ED A0 BD ED B8 80"))
        self.assertEqual((len(encoded), len(units), len(value.encode("utf-8"))),
                         (9, 4, 6))

    def test_constructed_jvm_numeric_and_preview_fields(self):
        # Explicit bit arithmetic checks the prose examples, not Java execution.
        self.assertEqual((0x40000001 * 4) & 0xffffffff, 4)
        self.assertEqual(int.from_bytes(bytes([255]), "big", signed=True), -1)
        self.assertEqual((-1) & 0xffff, 65535)
        self.assertEqual((32 & 31, 64 & 63), (0, 0))
        header = bytes.fromhex("CA FE BA BE FF FF 00 45")
        self.assertEqual(int.from_bytes(header[:4], "big"), 0xcafebabe)
        self.assertEqual((int.from_bytes(header[4:6], "big"),
                          int.from_bytes(header[6:8], "big")), (65535, 69))

    def test_constructed_cli_token_header_and_branch_coordinates(self):
        # CLI encoding arithmetic, not a metadata parser or verifier.
        token = 0x06000004
        self.assertEqual((token >> 24, token & 0xffffff), (6, 4))
        tiny = 0x1A
        self.assertEqual((tiny & 3, tiny >> 2), (2, 6))
        delta = int.from_bytes(bytes([0xFE]), "little", signed=True)
        self.assertEqual(0x10 + 2 + delta, 0x10)
        switch_next = 0x20 + 1 + 4 + 2 * 4
        self.assertEqual(switch_next, 0x2D)
        self.assertEqual([switch_next + n for n in (-13, 4)], [0x20, 0x31])
        # .un source interpretation does not make the destination unsigned.
        self.assertGreater(0xffffffff, 0x7fffffff)
        self.assertEqual(0x100000001 & 0xffffffff, 1)

    def test_constructed_ioctl_encoding_and_extents(self):
        # Encoding/length arithmetic, not dispatch or I/O-manager execution.
        device, access, function, method = 0x8000, 3, 0x801, 2
        code = (device << 16) | (access << 14) | (function << 2) | method
        self.assertEqual(code, 0x8000E006)
        self.assertEqual(((code >> 16) & 0xffff, (code >> 14) & 3,
                          (code >> 2) & 0xfff, code & 3),
                         (device, access, function, method))
        self.assertEqual(((code ^ 3) >> 2) & 0xfff, function)
        self.assertNotEqual(code ^ 3, code)  # Same function, different method.
        input_length, output_capacity = 8, 64
        self.assertEqual(max(input_length, output_capacity), 64)
        self.assertLessEqual(16, max(input_length, output_capacity))
        self.assertGreater(16, input_length)  # Fits allocation, not input.
        initialized_output, claimed_output = 8, 64
        self.assertGreater(claimed_output, initialized_output)

    def test_constructed_path_spelling_and_wchar_count(self):
        # A lexical counterexample, not a filesystem containment validator.
        root, candidate = "C:\\safe", "C:\\safe-other"
        self.assertTrue(candidate.startswith(root))
        self.assertFalse(candidate.startswith(root + "\\"))
        # W API counts code units; astral character needs a surrogate pair.
        spelling = "C:\\safe\\\U0001f600"
        units = len(spelling.encode("utf-16-le")) // 2
        self.assertEqual(units, len(spelling) + 1)
        required_capacity = units + 1  # Includes terminating NUL.
        self.assertEqual(required_capacity * 2,
                         len(spelling.encode("utf-16-le")) + 2)

    def test_constructed_mitigation_field_coordinates(self):
        # Field-specific bit interpretation, not a PE loader or OS policy test.
        optional = {0x0040: "dynamic_base", 0x4000: "guard_cf"}
        extended = {0x0001: "cet_compat", 0x0040: "forward_cfi_compat"}
        self.assertNotEqual(optional[0x0040], extended[0x0040])
        self.assertNotIn(0x0001, optional)
        base, offset = 0x10000000, 0x30
        self.assertEqual(offset % 16, 0)
        self.assertEqual(base + offset, 0x10000030)
        self.assertNotEqual(offset, base + offset)

    def test_constructed_mitigation_unknown_and_empty(self):
        # Do not turn a failed API's initialized buffer into an observation.
        def measured_flag(success, buffer_value):
            return bool(buffer_value) if success else None
        self.assertIsNone(measured_flag(False, 0))
        self.assertIs(measured_flag(True, 0), False)
        # Abstract documented EHCONT table stage, not all NtContinue rules:
        # prior shadow-stack check, process policy and audit are outside model.
        def table_stage(has_metadata, targets, address):
            return not has_metadata or address in targets
        self.assertTrue(table_stage(False, set(), 0x1200))
        self.assertFalse(table_stage(True, set(), 0x1200))
        self.assertTrue(table_stage(True, {0x1200}, 0x1200))
        self.assertFalse(table_stage(True, {0x1200}, 0x1300))

    def test_constructed_driver_terminal_owner(self):
        # Abstract atomic claim, not Windows cancellation or callback execution.
        for order in (("normal", "cancel"), ("cancel", "normal")):
            owner, completions = None, []
            for candidate in order:
                if owner is None:
                    owner = candidate
                    completions.append(candidate)
            self.assertEqual(completions, [order[0]])
        # Splitting check and claim admits the bad two-reader timeline.
        owner, ready, completions = None, {}, []
        for candidate, action in (("normal", "check"), ("cancel", "check"),
                                  ("normal", "claim"), ("cancel", "claim")):
            if action == "check":
                ready[candidate] = owner is None
            elif ready[candidate]:
                owner = candidate
                completions.append(candidate)
        self.assertEqual(completions, ["normal", "cancel"])
        # Both CANCELLED spellings have different handoff meanings.
        terminal_owner = {("mark_ex", "cancelled"): "caller",
                          ("unmark", "cancelled"): "cancel_callback"}
        self.assertNotEqual(terminal_owner[("mark_ex", "cancelled")],
                            terminal_owner[("unmark", "cancelled")])

    def test_constructed_partial_mdl_range(self):
        # Explicit half-open byte ranges, not an MDL or kernel API emulator.
        base, end, start = 0x1000, 0x2800, 0x1800
        def effective_length(address, length):
            if address < base or address >= end or length < 0:
                raise ValueError("outside source")
            actual = end - address if length == 0 else length
            if actual > end - address:
                raise ValueError("range exceeds source")
            return actual
        self.assertEqual(effective_length(start, 0), 0x1000)
        self.assertEqual(effective_length(start, 0x1000), 0x1000)
        for address, length in ((start, 0x1001), (end, 0), (base - 1, 1)):
            with self.assertRaises(ValueError):
                effective_length(address, length)
        # Data can change without changing a page's residence/identity.
        page = bytearray([8, 0, 0, 0])
        checked = page[0]
        page[0] = 255
        self.assertNotEqual(checked, page[0])

    def test_constructed_pool_flags_and_wait_status(self):
        flags = 0x100000000 | 0x40
        self.assertEqual(flags & 0xFFFFFFFF, 0x40)
        self.assertTrue(flags & 0x100000000)
        self.assertFalse((flags & 0xFFFFFFFF) & 0x100000000)
        # NTSTATUS sign-bit convention; not actual wait observations.
        statuses = {"success": 0, "timeout": 0x102,
                    "alerted": 0x101, "user_apc": 0xC0}
        self.assertTrue(all((value & 0x80000000) == 0 for value in statuses.values()))
        self.assertNotEqual(statuses["timeout"], statuses["success"])

    def test_constructed_appcontainer_grant_intersection(self):
        # Simplified allow-mask model, not an AccessCheck implementation.
        read, write = 1, 2
        user, container = read | write, read
        granted = user & container
        self.assertEqual(granted, read)
        self.assertFalse(granted & write)
        self.assertEqual(read & (read | write), read)
        # Mirror the pinned upstream test's arithmetic, not native execution.
        everyone, all_packages, restricted_packages = 3, 1, 2
        self.assertEqual(everyone & (all_packages | restricted_packages), 3)
        self.assertEqual(everyone & restricted_packages, 2)
        # Completed negative capability check must not become permission.
        for success, has_capability, allowed in (
                (True, True, True), (True, False, False),
                (False, True, False), (False, False, False)):
            self.assertEqual(success and has_capability, allowed)

    def test_constructed_wow64_layout_and_ec_varargs_ranges(self):
        # Explicit byte-layout model; native sizeof evidence is wow64-layout.c.
        wire32 = struct.pack('<IIII', 1, 0x11223344, 24, 7)
        wire64 = struct.pack('<I4xQQI4x', 1, 0x11223344, 24, 7)
        self.assertEqual(len(wire32), 16)
        self.assertEqual(len(wire64), 32)
        self.assertEqual(struct.unpack_from('<I', wire32, 4)[0], 0x11223344)
        self.assertEqual(struct.unpack_from('<Q', wire64, 8)[0], 0x11223344)
        self.assertEqual(struct.unpack_from('<I', wire32, 12)[0], 7)
        self.assertEqual(struct.unpack_from('<I', wire64, 24)[0], 7)
        with self.assertRaises(struct.error):
            struct.unpack('<I4xQQI4x', wire32)
        # Six ordinary 8-byte carriers: four in registers, two stacked.
        # A separate temporary backing a 3-byte aggregate is not added to X5.
        carriers, register_carriers, spill_bytes = 6, 4, 3
        stacked_bytes = (carriers - register_carriers) * 8
        self.assertEqual(stacked_bytes, 16)
        self.assertNotEqual(stacked_bytes, stacked_bytes + spill_bytes)

    def test_constructed_heap_ranges_and_failure_sentinel(self):
        # Range/sentinel model only; native API checks are in heap-contracts.c.
        old = bytes([0xA5] * 24)
        grown = old + bytes(40 - len(old))
        self.assertEqual(grown[:24], old)
        self.assertEqual(grown[24:], bytes(16))
        self.assertNotEqual(grown, bytes(40))
        self.assertEqual(len(grown[:16]), 16)
        failure64 = (1 << 64) - 1
        self.assertEqual(failure64, 0xFFFFFFFFFFFFFFFF)
        self.assertNotEqual(failure64, 0x00000000FFFFFFFF)
        self.assertEqual(64 - 20, 44)  # capacity is not initialized message length

    def test_constructed_eh_state_coordinates(self):
        # Decoded-integer arithmetic model, not FH4 bytes or Windows unwind execution.
        running_offset = 0
        offsets = []
        for delta in (4, 6, 12):
            running_offset += delta
            offsets.append(running_offset)
        self.assertEqual(offsets, [4, 10, 22])
        self.assertEqual([encoded - 1 for encoded in (0, 2, 3)], [-1, 1, 2])
        # A toy FH3-style transition map does not visit numeric intermediate states.
        cleanup = {2: (0, 'B'), 0: (-1, 'A')}
        state, actions = 2, []
        while state != -1:
            state, action = cleanup[state]
            actions.append(action)
        self.assertEqual(actions, ['B', 'A'])
        # Different return-value domains, not an attempt to call a runtime handler.
        filter_search, disposition_search = 0, 1
        self.assertNotEqual(filter_search, disposition_search)

    def test_constructed_threadpool_notification_accounting(self):
        # Logical obligation model only, not Windows TP_IO internals/execution.
        def disposition(issue_result, skip_success):
            if issue_result == 'issue_failure':
                return 'cancel_notification'
            if issue_result == 'immediate_success' and skip_success:
                return 'cancel_notification'
            return 'callback'

        for skip in (False, True):
            self.assertEqual(disposition('pending', skip), 'callback')
            self.assertEqual(disposition('issue_failure', skip), 'cancel_notification')
        self.assertEqual(disposition('immediate_success', False), 'callback')
        self.assertEqual(disposition('immediate_success', True), 'cancel_notification')
        # One modeled start obligation needs exactly one disposition.
        for issue in ('issue_failure', 'immediate_success', 'pending'):
            for skip in (False, True):
                action = disposition(issue, skip)
                callbacks = int(action == 'callback')
                cancels = int(action == 'cancel_notification')
                self.assertEqual(1 - callbacks - cancels, 0)
        self.assertEqual(1 - 1 - 1, -1)  # double disposition, not an API counter
        self.assertEqual(4096 - 24, 4072)
        self.assertEqual(0x100000007 & 0xffffffff, 7)

    def test_ndr64_constructed_array_count_bytes(self):
        # Constructed fragment arithmetic only; not runtime acceptance or a PDU.
        counts = struct.pack('<QQQ', 8, 0, 3)
        self.assertEqual(len(counts), 24)
        self.assertEqual(counts[:8], b'\x08' + b'\x00' * 7)
        fragment = counts + b'abc'
        self.assertEqual(len(fragment), 27)
        self.assertEqual(struct.unpack('<QQQ', fragment[:24]), (8, 0, 3))
        self.assertEqual(fragment[24:], b'abc')
        self.assertEqual(len(struct.pack('<QQQ', 0, 0, 0)), 24)
        # Virtual argument slots are not wire byte coordinates.
        self.assertEqual([slot * 8 for slot in range(1, 5)], [8, 16, 24, 32])
        self.assertEqual([slot * 4 for slot in range(1, 5)], [4, 8, 12, 16])

    def test_com_constructed_slot_and_argument_models(self):
        # Arithmetic/list model only: not COM ABI execution or IDispatch.
        first_added_slot = 3
        self.assertEqual(first_added_slot * 4, 12)
        self.assertEqual(first_added_slot * 8, 24)
        source_order = ['a', 'b', 'c']
        positional_rgvarg = list(reversed(source_order))
        self.assertEqual(positional_rgvarg, ['c', 'b', 'a'])
        self.assertEqual(positional_rgvarg[0], source_order[2])
        # Named arguments and property puts are deliberately not modeled.

    def test_ndr_constructed_element_range_models(self):
        # Arithmetic only: not an RPC runtime, wire decoder or live call.
        capacity, transmitted, element_bytes = 8, 3, 2
        self.assertEqual(capacity * element_bytes, 16)
        self.assertEqual(transmitted * element_bytes, 6)
        self.assertLess(transmitted * element_bytes, capacity * element_bytes)

        def valid_elements(first, count, extent):
            return (0 <= first <= extent and 0 <= count <= extent - first)

        self.assertTrue(valid_elements(2, 3, 8))
        self.assertEqual(list(range(2, 2 + 3)), [2, 3, 4])
        self.assertFalse(valid_elements(7, 2, 8))
        self.assertTrue(valid_elements(8, 0, 8))
        self.assertFalse(valid_elements(-1, 1, 8))
        self.assertFalse(valid_elements(1, -1, 8))
        self.assertTrue(0 <= 32 <= 1024)
        self.assertFalse(valid_elements(0, 32, 16))

    def test_windows_mapping_coordinate_and_record_models(self):
        # Constructed arithmetic only; no Windows mapping or peer process.
        granularity, offset, size = 0x10000, 0x23456, 0x300
        aligned = (offset // granularity) * granularity
        delta = offset - aligned
        self.assertEqual((aligned, delta, delta + size), (0x20000, 0x3456, 0x3756))
        self.assertEqual(offset + size, 0x23756)
        self.assertEqual(aligned + delta + size, offset + size)
        self.assertEqual(0x10000000 + 0x120, 0x10000120)
        self.assertEqual(0x70000000 + 0x120, 0x70000120)
        self.assertNotEqual(0x10000120, 0x70000120)

        def valid_range(start, length, retained_extent):
            return (0 <= start <= retained_extent
                    and 0 <= length <= retained_extent - start)

        self.assertTrue(valid_range(0, 64, 4096))
        self.assertFalse(valid_range(0, 64, 48))
        self.assertFalse(valid_range(0xff0, 0x20, 0x1000))
        self.assertTrue(valid_range(0x1000, 0, 0x1000))

    def test_windows_handle_flag_and_selection_models(self):
        # Constructed property/set models, not Win32 calls or child creation.
        def properties(old, change_mask, desired):
            return (old & ~change_mask) | (desired & change_mask)

        self.assertEqual(properties(3, 1, 0), 2)
        self.assertEqual(properties(3, 0, 0), 3)
        inheritable = {'pipe', 'secret-file'}
        explicit_list = {'pipe'}
        self.assertEqual(inheritable & explicit_list, {'pipe'})
        self.assertIn('secret-file', inheritable)
        source_rights, desired_rights = {'READ', 'WRITE'}, {'READ'}
        same_access_grant = source_rights.copy()
        self.assertIn('WRITE', same_access_grant)
        self.assertNotEqual(same_access_grant, desired_rights)

    def test_windows_access_mask_and_order_models(self):
        # Restricted toy models, NOT Windows AccessCheck or token execution.
        generic_read, explicit, mapping = 0x80000000, 2, 5
        request = generic_read | explicit
        mapped = (request & ~generic_read) | mapping
        self.assertEqual(mapped, 7)
        self.assertEqual({'READ', 'WRITE'} & {'READ'}, {'READ'})
        self.assertNotEqual({'READ', 'WRITE'} | {'READ'}, {'READ'})

        def ordinary_dacl(requested, applicable_aces):
            # All ACEs apply; mapped rights; no owner/privilege/MIC/other rules.
            remaining = requested
            for kind, mask in applicable_aces:
                if kind == 'deny' and remaining & mask:
                    return False
                if kind == 'allow':
                    remaining &= ~mask
                if remaining == 0:
                    return True
            return False

        self.assertTrue(ordinary_dacl(1, [('allow', 1), ('deny', 1)]))
        self.assertFalse(ordinary_dacl(1, [('deny', 1), ('allow', 1)]))
        self.assertFalse(ordinary_dacl(3, [('allow', 1)]))
        self.assertTrue(ordinary_dacl(3, [('allow', 1), ('allow', 2)]))

    def test_flow_ranges_and_partial_store(self):
        # Constructed byte-addressed memory, not target instruction execution.
        self.assertEqual({x & 15 for x in range(256)}, set(range(16)))
        field = bytearray((0x11223344).to_bytes(4, 'little'))
        field[2:4] = (0xabcd).to_bytes(2, 'little')
        self.assertEqual(int.from_bytes(field, 'little'), 0xabcd3344)
        self.assertEqual(set(range(8, 12)) & set(range(10, 12)), {10, 11})
        self.assertFalse(set(range(8, 12)) & set(range(12, 14)))

    def test_path_correlations_and_machine_width(self):
        # Finite constructed models; no solver or specimen is executed.
        pairs = {(4, 8), (16, 32)}
        self.assertTrue(all(length <= capacity for length, capacity in pairs))
        self.assertNotIn((16, 8), pairs)
        self.assertGreater(16, 8)
        self.assertFalse(any(n < 8 and n >= 8 for n in range(256)))
        self.assertTrue(7 < 8 and 9 >= 8)  # Different value versions.
        body, i = [], 0
        while i < 4:
            body.append(i)
            i += 1
        self.assertEqual(body, [0, 1, 2, 3])
        self.assertEqual(i, 4)
        self.assertEqual((255 + 1) & 255, 0)
        self.assertTrue(((255 + 1) & 255) <= 16)
        self.assertFalse(255 + 1 <= 16)
        self.assertTrue(-1 < 16)
        self.assertFalse(255 < 16)

    def test_runtime_helper_return_models(self):
        # Mathematical contracts only; no GCC runtime binary is executed.
        def compare_encoding(left, right):
            return 0 if left < right else 2 if left > right else 1

        self.assertEqual([compare_encoding(a, 5) for a in (4, 5, 6)], [0, 1, 2])
        for left in range(-8, 9):
            for right in range(-8, 9):
                result = compare_encoding(left, right)
                self.assertEqual(result == 1, left == right)
                self.assertEqual(result < 1, left < right)
                self.assertEqual(result != 0, left >= right)
        self.assertEqual(divmod(17, 5), (3, 2))
        self.assertEqual(17, 5 * 3 + 2)
        # The same eight-bit bits differ under signed/unsigned interpretation.
        self.assertEqual(compare_encoding(255, 1), 2)
        self.assertEqual(compare_encoding(-1, 1), 0)

    def test_cpp_dispatch_coordinates(self):
        # Constructed coordinates only, not a compiler/ABI execution test.
        address_point, pointer_bytes = 0x5000, 8
        self.assertEqual(address_point - 2 * pointer_bytes, 0x4ff0)
        self.assertEqual(address_point - pointer_bytes, 0x4ff8)
        subobject, top_delta = 0x1020, -32
        self.assertEqual(subobject + top_delta, 0x1000)
        self.assertEqual(subobject + top_delta + 0x38, 0x1038)
        self.assertEqual(subobject + 0x38, 0x1058)
        self.assertEqual(0x2000 + 0x18, 0x2018)
        member_ptr, adjustment = 17, 32
        self.assertEqual(0x1000 + adjustment, 0x1020)
        self.assertEqual((member_ptr - 1) // pointer_bytes, 2)
        self.assertEqual(0x1000 + 0x10 + 0x30, 0x1040)
        locator, self_rva, type_rva = 0x140003000, 0x3000, 0x5000
        image_base = locator - self_rva
        self.assertEqual(image_base, 0x140000000)
        self.assertEqual(image_base + type_rva, 0x140005000)
        self.assertNotEqual(locator + type_rva, image_base + type_rva)
        self.assertEqual(subobject - 32, 0x1000)

    def test_structure_layout_constraints(self):
        # Stated layout assumptions only, not target compiler layout verification.
        def layout(fields, packing):
            offsets, cursor, record_alignment = [], 0, 1
            for size, natural_alignment in fields:
                alignment = min(natural_alignment, packing)
                record_alignment = max(record_alignment, alignment)
                cursor = (cursor + alignment - 1) // alignment * alignment
                offsets.append(cursor)
                cursor += size
            size = (cursor + record_alignment - 1) // record_alignment * record_alignment
            return offsets, size

        fields = [(1, 1), (4, 4), (2, 2)]
        self.assertEqual(layout(fields, 16), ([0, 4, 8], 12))
        self.assertEqual(layout(fields, 1), ([0, 1, 5], 7))
        inner_offsets, inner_size = layout([(1, 1), (4, 4)], 16)
        self.assertEqual((inner_offsets, inner_size), ([0, 4], 8))
        outer_offsets, outer_size = layout([(1, 1), (inner_size, 4)], 1)
        self.assertEqual(outer_offsets[1] + inner_offsets[1], 5)
        self.assertEqual(outer_size, 9)
        self.assertEqual(0x10 + 8, 0x18)
        self.assertEqual(20 + 4, 24)
        self.assertEqual(2 * 16, 32)
        accesses = set(range(0, 2)) | set(range(4, 8)) | set(range(16, 24))
        self.assertEqual(set(range(24)) - accesses, set(range(2, 4)) | set(range(8, 16)))

    def test_dispatch_and_alignment_examples(self):
        # Constructed arithmetic, not a disassembler, assembler or CPU run.
        entry = 0xffffffe0
        signed_entry = entry - (1 << 32)
        self.assertEqual(0x4000 + signed_entry, 0x3fe0)
        self.assertEqual(0x4000 + entry, 0x100003fe0)
        for x in list(range(32)) + [0x7fffffff, 0x80000000, 0xffffffff]:
            self.assertEqual(((x - 10) & 0xffffffff) <= 3, 10 <= x <= 13)
        self.assertEqual((9 - 10) & 0xffffffff, 0xffffffff)
        skip = (-0x1003) % 16
        self.assertEqual(skip, 13)
        self.assertGreater(skip, 7)
        self.assertEqual(0x1003 + skip, 0x1010)

    def test_transformed_loop_ranges(self):
        # Model the stated access domain, not compiler-generated instructions.
        for n in range(65):
            vector_end = 4 * (n // 4)
            vector_bytes = set()
            for element in range(0, vector_end, 4):
                vector_bytes.update(range(element * 4, element * 4 + 16))
            tail_bytes = set()
            for element in range(vector_end, n):
                tail_bytes.update(range(element * 4, element * 4 + 4))
            self.assertFalse(vector_bytes & tail_bytes)
            self.assertEqual(vector_bytes | tail_bytes, set(range(4 * n)))
        self.assertEqual(4 * 6, 24)
        self.assertEqual(16 + 16, 32)
        addresses = [12 * i for i in range(4)]
        self.assertEqual(addresses, [0, 12, 24, 36])
        self.assertEqual(addresses[-1] + 8, 44)

    def test_riscv_constructed_values(self):
        # Pure arithmetic model; no RISC-V instructions are executed.
        mask64 = (1 << 64) - 1
        sign32 = lambda n: (n & 0x7fffffff) - (n & 0x80000000)
        self.assertEqual(sign32(0x80000000) & mask64, 0xffffffff80000000)
        self.assertEqual(0x80000000 & 0xffffffff, 0x0000000080000000)
        self.assertEqual(1 << (32 & 63), 0x100000000)
        self.assertEqual(sign32(1 << (32 & 31)), 1)
        self.assertLess(sign32(0xffffffff), 1)
        self.assertGreater(0xffffffff, 1)
        self.assertEqual((0x1003 + 0) & ~1, 0x1002)
        self.assertNotEqual(0x1002 % 4, 0)
        self.assertEqual(0x1002 % 2, 0)
        self.assertEqual(0x2002 + 2, 0x2004)
        self.assertEqual(0x2002 + 4, 0x2006)

    def test_riscv_pcrel_split(self):
        # Check sign-boundary rounding and recombination, not linker output.
        for delta in (-0x1801, -0x1800, -0x801, -0x800, -1, 0,
                      0x7ff, 0x800, 0x17ff, 0x1800, 0x1801):
            high = (delta + 0x800) >> 12
            low = (delta & 0xfff)
            if low & 0x800:
                low -= 0x1000
            self.assertTrue(-2048 <= low <= 2047)
            self.assertEqual((high << 12) + low, delta)
        self.assertEqual((0x1800 + 0x800) >> 12, 2)
        self.assertEqual(0x1000 + 0x2000 - 0x800, 0x2800)
        self.assertEqual(0x1000 + 0x1000 - 0x800, 0x1800)

    def test_aarch64_numeric_examples(self):
        # Constructed arithmetic, not execution of A64 instructions.
        self.assertEqual(0xffffffff & 0xffffffff, 0x00000000ffffffff)
        signed_halfword = int.from_bytes(bytes.fromhex("01 00"), "little", signed=True)
        self.assertEqual((32767 + signed_halfword) & 0xffffffff, 32768)
        page_base = (0x12345 & ~0xfff) + (2 << 12)
        self.assertEqual(page_base, 0x14000)
        self.assertEqual(page_base + 0x678, 0x14678)
        self.assertEqual(0x12345 + (2 << 12) + 0x678, 0x149bd)
        self.assertEqual(0x1000 + 8, 0x1008)
        # A64 subtraction C is the complement of unsigned borrow.
        for a in range(256):
            for b in range(256):
                carry = a >= b
                zero = ((a - b) & 255) == 0
                self.assertEqual(not carry, a < b)
                self.assertEqual(carry and not zero, a > b)

    def test_x86_numeric_examples(self):
        # Arithmetic models only: no target instruction execution.
        original = 0x1122334455667788
        self.assertEqual(original & ~0xff, 0x1122334455667700)
        self.assertEqual(original & ~0xffff, 0x1122334455660000)
        self.assertEqual((-128) & 0xffffffff, 0x00000000ffffff80)
        self.assertEqual((-128) & 0xffffffffffffffff, 0xffffffffffffff80)
        self.assertEqual(0x1000 + 7 - 0x20, 0xfe7)
        self.assertEqual(32 & 31, 0)
        self.assertEqual(33 & 31, 1)
        self.assertEqual(-5 // 2, -3)
        self.assertEqual(math.trunc(-5 / 2), -2)
        self.assertEqual(0xffffffff * 2, 0x1fffffffe)
        self.assertEqual((-1 * 2) & 0xffffffff, 0xfffffffe)
        self.assertEqual(((1 << 32) | 0) // 2, 0x80000000)
        self.assertEqual(3 * 8, 24)

    def test_x86_comparison_predicates(self):
        # Exhaustive 8-bit arithmetic check of documented CMP predicates.
        # This does not execute CMP/Jcc on the host or a target CPU.
        for a in range(256):
            for b in range(256):
                result = (a - b) & 255
                cf = a < b
                zf = result == 0
                sf = bool(result & 128)
                of = bool((a ^ b) & (a ^ result) & 128)
                signed_a = a if a < 128 else a - 256
                signed_b = b if b < 128 else b - 256
                self.assertEqual(not cf and not zf, a > b)
                self.assertEqual(cf or zf, a <= b)
                self.assertEqual(sf != of, signed_a < signed_b)
                self.assertEqual(sf == of, signed_a >= signed_b)
                self.assertEqual(zf or sf != of, signed_a <= signed_b)
                self.assertEqual(not zf and sf == of, signed_a > signed_b)

    def test_aarch32_address_and_alignment_examples(self):
        # Constructed coordinate arithmetic, not instruction execution.
        self.assertEqual(0x1002 + 4, 0x1006)
        self.assertEqual(0x2001 & ~1, 0x2000)
        self.assertEqual(((0x1002 + 4) & ~3) + 0x20, 0x1024)
        self.assertEqual(0x1002 + 4 + 0x20, 0x1026)
        self.assertEqual(0x1018 - 0x1010, 8)
        self.assertEqual(0x7ffc % 4, 0)
        self.assertNotEqual(0x7ffc % 8, 0)
        self.assertEqual((1 + 1) & ~1, 2)  # r1 rounds to even r2.
        self.assertEqual(3 - (4 - 2), 1)  # Three words, two remaining registers.

    def test_endian_and_signed_interpretations(self):
        raw = bytes.fromhex("01 00 00 80")
        self.assertEqual(int.from_bytes(raw, "little"), 2147483649)
        self.assertEqual(int.from_bytes(raw, "big"), 16777344)
        self.assertEqual(int.from_bytes(raw, "little", signed=True), -2147483647)

    def test_mips_constructed_values(self):
        # Arithmetic only, not execution on a MIPS core or linker.
        self.assertEqual(0x1000 + 4 + 3 * 4, 0x1010)
        self.assertEqual(0x2000 + 8, 0x2008)
        immediate = int.from_bytes(bytes.fromhex("ff ff"), "little", signed=True)
        self.assertEqual((1 + immediate) & 0xffffffff, 0)
        self.assertEqual((0x7fffffff + 1) & 0xffffffff, 0x80000000)
        signed_int = 0x80000000 - (1 << 32)
        self.assertEqual(signed_int & ((1 << 64) - 1), 0xffffffff80000000)
        self.assertEqual((0x1235 << 16) - 0x8000, 0x12348000)
        self.assertEqual((0x1234 << 16) - 0x8000, 0x12338000)

    def test_powerpc_constructed_values(self):
        # Arithmetic models only; no ABI/compiler/CPU execution is claimed.
        source = 0x12345678
        rotated = ((source << 8) | (source >> 24)) & 0xffffffff
        self.assertEqual(rotated, 0x34567812)
        mask = sum(1 << (31 - bit) for bit in range(24, 32))
        self.assertEqual(mask, 0xff)
        self.assertEqual(rotated & mask, 0x12)
        self.assertEqual(source & mask, 0x78)
        self.assertEqual(0x2000 + 4, 0x2004)
        self.assertEqual(0x8000 + 8, 0x8008)
        self.assertEqual(0x7ff8 % 8, 0)
        self.assertNotEqual(0x7ff8 % 16, 0)
        self.assertEqual(0x80000000 & 0xffffffff, 0x0000000080000000)

    def test_service_boundary_constructed_values(self):
        # Representation arithmetic only, not actual syscall execution.
        offset = 0x1122334455667788
        low, high = offset & 0xffffffff, offset >> 32
        self.assertEqual((low, high), (0x55667788, 0x11223344))
        self.assertEqual((high << 32) | low, offset)
        mask = (1 << 64) - 1
        for value in (-4096, -4095, -13, -1, 0, 1, 4095):
            self.assertEqual((value & mask) >= (-4095 & mask), -4095 <= value <= -1)

    def test_extension_and_truncation(self):
        self.assertEqual(int.from_bytes(b"\x80", "little", signed=True), -128)
        self.assertEqual((-128) & 0xffffffff, 0xffffff80)
        self.assertEqual(0xffffff80 & 0xff, 0x80)
        self.assertEqual(0x00000080 & 0xff, 0x80)

    def test_integer_allocation_mismatch(self):
        wide = 0x40000001 * 4
        self.assertEqual(wide, 0x100000004)
        self.assertEqual(wide & 0xffffffff, 4)
        self.assertEqual(65537 & 0xffff, 1)

    def test_range_and_alignment_checks(self):
        def fits(offset, width, total):
            return 0 <= offset <= total and 0 <= width <= total - offset
        self.assertFalse(fits(12, 8, 16))
        self.assertFalse(fits(17, 0, 16))
        self.assertTrue(fits(16, 0, 16))
        maximum = 0xffffffff
        self.assertGreater(maximum + 15, maximum)
        self.assertEqual((17 + 15) & ~15, 32)

    def test_pe_coordinates(self):
        self.assertEqual(0x600 + (0x2120 - 0x2000), 0x720)
        self.assertGreater(0x23f0 - 0x2000 + 0x20, 0x400)
        self.assertTrue(0x400 <= 0x2500 - 0x2000 < 0x900)
        self.assertEqual(0x180000000 + 0x2120, 0x180002120)

    def test_elf_coordinates(self):
        self.assertEqual(0x1000 + (0x4120 - 0x4000), 0x1120)
        self.assertGreater(0x44f0 - 0x4000 + 0x20, 0x500)
        self.assertTrue(0x500 <= 0x4600 - 0x4000 < 0x900)
        self.assertEqual(0x70000000 + 0x4120, 0x70004120)

    def test_macho_coordinates(self):
        offset = 0x1000 + (0x100001180 - 0x100001000)
        self.assertEqual(offset, 0x1180)
        self.assertEqual(0x4000 + offset, 0x5180)
        self.assertEqual(0x100001180 + 0x200000, 0x100201180)
        self.assertGreater(0x3f0 + 0x20, 0x400)

    def test_binary32_and_nan_examples(self):
        # struct's f format is IEEE binary32; this is not a target CPU test.
        rounded = struct.unpack("<f", struct.pack("<f", 16777217))[0]
        self.assertEqual(rounded, 16777216)
        value = math.nan
        self.assertFalse(value < 0 or value > 100)
        self.assertFalse(math.isfinite(value))
        self.assertFalse(math.isfinite(math.inf))

    def test_macho_highvm_and_chain_stride(self):
        backed_start = 0x1000 + (0x3000 - 0x1000)
        self.assertEqual(backed_start, 0x3000)
        self.assertEqual(0x800 + (0x3100 - backed_start), 0x900)
        self.assertEqual(3 * 4, 12)
        self.assertEqual(3 * 8, 24)

    def test_quota_subtraction_matches_nonoverflowing_sum(self):
        # Exhaustive small nonnegative domain, not a concurrent target test.
        for limit in range(16):
            for used in range(20):
                for reserved in range(20):
                    for cost in range(20):
                        checked = (used <= limit and reserved <= limit - used
                                   and cost <= limit - used - reserved)
                        self.assertEqual(checked, used + reserved + cost <= limit)


if __name__ == "__main__":
    unittest.main()
