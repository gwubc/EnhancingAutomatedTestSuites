def test_cherry_picking_loader_exec_module(self):
        loader = _CherryPickingLoader()
        module = loader.create_module(self.spec)
        loader.exec_module(module)
        self.parse_attr_map.assert_called_with(self.attr_map, self.spec.name)
        for key in self.cherry_pick_map.identifiers.keys():
            expect = getattr(module, key)
            self.assertEqual(expect, _CHERRY_PICK)
        for key, expect in self.additional_attrs.items():
            val = getattr(module, key)
            self.assertEqual(expect, val)
        self.assertEqual(self.all_value, module.__all__)