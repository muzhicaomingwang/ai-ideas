package com.teamventure.adapter.web.suppliers;

import com.teamventure.adapter.web.common.ApiResponse;
import com.teamventure.app.service.AuthService;
import com.teamventure.app.service.SupplierService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/suppliers")
public class SupplierController {

    private final AuthService authService;
    private final SupplierService supplierService;

    public SupplierController(AuthService authService, SupplierService supplierService) {
        this.authService = authService;
        this.supplierService = supplierService;
    }

    @GetMapping
    public ApiResponse<?> search(@RequestHeader("Authorization") String authorization,
                                 @RequestParam(required = false) String city,
                                 @RequestParam(required = false) String category) {
        authService.getUserIdFromAuthorization(authorization);
        return ApiResponse.success(supplierService.search(city, category));
    }

    @GetMapping("/{supplierId}")
    public ApiResponse<?> detail(@RequestHeader("Authorization") String authorization,
                                 @PathVariable String supplierId) {
        authService.getUserIdFromAuthorization(authorization);
        return ApiResponse.success(supplierService.getById(supplierId));
    }
}

